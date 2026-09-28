# OpenAI audio


## Text to speech  

OpenAI has three text-to-speech (TTS) models. The newest is  
`gpt-4o-mini-tts`, which accepts natural-language instructions about  
delivery. The older `tts-1` (lower latency) and `tts-1-hd` (higher  
quality) models take no instructions but use the same endpoint, so you  
switch by changing the model name.  

TTS models take text only and return audio only. The response body holds  
the encoded audio, so you can write the bytes straight to disk. Supported  
formats are `mp3` (default), `opus`, `aac`, `flac`, `wav`, and `pcm`.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input="Dobrý deň, vitajte na stránke ZetCode!",
    response_format="wav",
)

with open("hello.wav", "wb") as f:
    f.write(response.content)

print("Saved hello.wav")
```

The `input` is read verbatim. The voices are optimised for English, but  
the model follows Whisper's language list, which includes Slovak. OpenAI's  
usage policies also require you to tell end users that the voice is  
AI-generated.  

The 13 built-in voices are `alloy`, `ash`, `ballad`, `coral`, `echo`,  
`fable`, `nova`, `onyx`, `sage`, `shimmer`, `verse`, `marin`, and `cedar`.  
OpenAI recommends `marin` or `cedar` for the best quality. The `tts-1`  
models support only a smaller set (`alloy`, `ash`, `coral`, `echo`,  
`fable`, `onyx`, `nova`, `sage`, and `shimmer`). Approved custom voices  
can be created from a consent recording and used by passing their ID as  
`voice`.  

## Transcription models  

Speech-to-text lives in `client.audio.transcriptions`. Start with  
`gpt-transcribe`, which OpenAI recommends for recorded speech in its  
original language. Specialised models cover the rest: `gpt-4o-transcribe-diarize`  
for speaker labels and `whisper-1` for word timestamps, subtitle formats,  
and translation into English. The older `gpt-4o-transcribe` and  
`gpt-4o-mini-transcribe` still work.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("aesop_cat_mice.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
        extra_body={"languages": ["sk"]},
    )

print(transcription.text)
print(transcription.languages)
```

`gpt-transcribe` takes a `languages` list instead of the single  
`language` field, and you must not send both. The SDK has no typed  
argument for it yet, so it goes through `extra_body`. The response has  
the detected languages, for example `[{"code": "sk"}]`, and an empty  
list when the model can't decide. Omit `languages` to rely on automatic  
detection. Files are limited to 25 MB and can be mp3, mp4, mpeg, mpga,  
m4a, wav, or webm.  

## Speaker diarization  

The model `gpt-4o-transcribe-diarize` labels who is speaking. It needs  
`response_format="diarized_json"`, and for audio longer than 30 seconds  
you must also set `chunking_strategy`.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("interview.mp3", "rb") as audio_file:
    result = client.audio.transcriptions.create(
        model="gpt-4o-transcribe-diarize",
        file=audio_file,
        response_format="diarized_json",
        chunking_strategy="auto",
    )

for seg in result.segments:
    print(f"[{seg.speaker}] ({seg.start:.2f} -> {seg.end:.2f}) {seg.text}")
```

Timestamps are per segment, not per word. You can pass up to four short  
reference clips (2-10 seconds each) with `known_speaker_names` and  
`known_speaker_references` to map segments onto known people. Both are  
data URLs sent through `extra_body`. This model does not accept a  
`prompt`, and diarization is not available in realtime sessions.  

## Word timestamps  

Word-level timing is available only with `whisper-1`. Request the  
`verbose_json` format and list the `word` granularity.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("interview.mp3", "rb") as audio_file:
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["word"],
    )

for w in result.words:
    print(f"({w.start:.2f} -> {w.end:.2f}) {w.word}")
```

The same endpoint family has `client.audio.translations`, which turns  
speech in another language into English text. It also works only with  
`whisper-1`.  

## Context, keywords, and prompts  

I found no equivalent of Gemini's SMART mode in the docs. The context  
features of `gpt-transcribe` are three optional inputs. `prompt` gives  
free-form context about the recording, `keywords` lists literal terms you  
expect to hear, and `languages` lists the expected languages.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("meeting.mp3", "rb") as audio_file:
    plain = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
    )

print("--- PLAIN ---")
print(plain.text)

with open("meeting.mp3", "rb") as audio_file:
    biased = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
        prompt="A technical talk about a Python tutorial site.",
        extra_body={
            "keywords": ["ZetCode", "Pydantic", "Kubernetes"],
            "languages": ["sk", "en"],
        },
    )

print("--- WITH CONTEXT ---")
print(biased.text)
```

Keywords are hints, not required output, so include only terms that are  
really spoken. Keep each keyword on one line and avoid `<`, `>`, and line  
breaks, because the API rejects the whole request otherwise. `whisper-1`  
still accepts a `prompt`, but it is capped at 224 tokens and gives less  
control.  

## Streaming transcription  

With `stream=True` the file is transcribed incrementally, so long  
recordings show text almost at once. `gpt-transcribe` and the older  
`gpt-4o` models support this, but `whisper-1` does not.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

with open("aesop_cat_mice.mp3", "rb") as audio_file:
    stream = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
        extra_body={"languages": ["sk"]},
        stream=True,
    )

    for event in stream:
        if event.type == "transcript.text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "transcript.text.done":
            print("\n--- done ---")
```

This streams a finished recording. For audio that is still arriving from  
a microphone or a call, OpenAI points to its Realtime transcription guide  
and the `gpt-live-transcribe` model.  

## Round trip: speech to text and back  

As in the Gemini example, we synthesize a Slovak sentence, save it as  
WAV, and check what the transcription model heard.  

```python
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

original = "Bratislava je hlavné mesto Slovenska."

tts = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="sage",
    input=original,
    response_format="wav",
)

with open("roundtrip.wav", "wb") as f:
    f.write(tts.content)

with open("roundtrip.wav", "rb") as audio_file:
    stt = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=audio_file,
        extra_body={"languages": ["sk"]},
    )

print("Original:   ", original)
print("Transcribed:", stt.text.strip())
print("Match:      ", original.strip() == stt.text.strip())
```

## GPT-Live: talking to the model  

For new voice applications OpenAI recommends GPT-Live (`gpt-live-1`),  
which replaces my earlier Realtime example. It is full duplex, so it can  
listen while it speaks. It also hands longer work (lookups, tools) to a  
backend model, which is called delegation, while the conversation goes on.  
Sessions are billed by duration.  

A server connects to `wss://api.openai.com/v1/live/sessions`. It sends  
`session.start` first and waits for `session.started`. The session then  
streams base64 audio in both directions: 24 kHz, 16-bit mono PCM is the  
default, and a session uses one format for input and output. Unlike the  
Gemini Live example, there is no text input. Everything is audio, so we  
synthesize the question with TTS and feed it in at real-time speed.  

```python
import asyncio
import base64
import os
import wave

from openai import AsyncOpenAI, OpenAI

api_key = os.getenv("OPENAI_API_KEY")

# 1. Synthesize the user's question as raw 24 kHz PCM
tts = OpenAI(api_key=api_key).audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="ash",
    input="Hello! Tell me a fun fact about Slovakia.",
    response_format="pcm",
)
question = tts.content + b"\x00\x00" * 24000  # 1 s of silence ends the turn

session = {
    "model": "gpt-live-1",
    "instructions": "You are a friendly assistant. Be brief.",
    "audio": {
        "format": {"type": "audio/pcm", "rate": 24000},
        "output": {"voice": "marin"},
    },
    "delegation": {
        "type": "responses",
        "responses": {
            "model": "gpt-5.6-luna",
            "tools": [{"type": "web_search"}],
            "tool_choice": "auto",
        },
    },
}


async def feed(conn):
    # Pace the audio like a live microphone: 4800 bytes = 0.1 s
    for i in range(0, len(question), 4800):
        chunk = question[i:i + 4800]
        await conn.session.input_audio.append(
            audio=base64.b64encode(chunk).decode("ascii")
        )
        await asyncio.sleep(0.1)

    await asyncio.sleep(10)  # leave time for the spoken reply
    await conn.session.close()


async def main():
    tasks = []

    with wave.open("live_reply.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)

        async with AsyncOpenAI(api_key=api_key) as client:
            async with client.live.connect() as conn:
                await conn.session.start(session=session,
                                         event_id="event_start")

                async for event in conn:
                    if event.type == "session.started":
                        tasks.append(asyncio.create_task(feed(conn)))

                    elif event.type == "session.output_audio.delta":
                        wf.writeframes(base64.b64decode(event.delta))

                    elif event.type == "session.output_transcript.delta":
                        print(event.delta, end="", flush=True)

                    elif event.type == "session.closed":
                        print("\nUsage:", event.usage)
                        break

    for t in tasks:
        t.cancel()
    print("Saved live_reply.wav")


asyncio.run(main())
```

Always end a session with `session.close` and keep reading until  
`session.closed` arrives, because it carries the final usage numbers.  
The documented example uses a Responses backend with web search, and I  
kept it. Backend usage is billed separately from the voice time. The  
other formats are 16 kHz PCM and 8 kHz G.711 μ-law or A-law for  
telephony. Browsers should use WebRTC instead of a raw WebSocket, and  
phone calls go through SIP.  

The older Realtime API still exists (the docs' examples now use  
`gpt-realtime-2.1`), but I didn't verify its current event names, so I  
left it out.  

I adapted the GPT-Live example from OpenAI's stdin/stdout sample instead  
of copying it. The pacing and the 10-second wait are my own additions, and  
I couldn't run any of it here. Test it with a real key before publishing  
it. The docs also say you need an SDK version with Live support.
