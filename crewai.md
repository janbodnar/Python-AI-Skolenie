# CrewAI

CrewAI is a cutting-edge Python framework designed for orchestrating role-playing,  
autonomous AI agents. It enables teams of AI agents to collaborate seamlessly on  
complex tasks by leveraging individual expertise and collective intelligence.  

By fostering collaborative intelligence, CrewAI empowers developers to create  
sophisticated multi-agent systems that can tackle intricate problems requiring  
diverse skills and perspectives.  

```bash
pip install crewai
```

## What are AI Agents?

AI agents are autonomous software systems that can perceive their environment,  
make decisions, and take actions to achieve specific objectives. Unlike traditional  
programs that follow predetermined instructions, AI agents can:  

- **Reason and Plan**: Break down complex goals into manageable subtasks  
- **Learn and Adapt**: Improve performance through interaction and feedback  
- **Communicate**: Share information and coordinate with other agents  
- **Use Tools**: Access external systems, APIs, and resources  
- **Make Decisions**: Choose appropriate actions based on current context  

Think of an AI agent as a digital team member with specialized knowledge and  
the ability to work independently or collaboratively to solve problems.  

## CrewAI Library Overview

CrewAI transforms the concept of AI agents into a practical framework where  
multiple agents work together as a crew. Each agent has:  

- **Defined Role**: Clear responsibilities and expertise area  
- **Specific Goals**: Measurable objectives to accomplish  
- **Backstory**: Context that influences decision-making  
- **Tools**: Access to external resources and capabilities  
- **Memory**: Ability to retain and use information from past interactions  

The library provides a structured approach to multi-agent collaboration,  
handling task delegation, communication protocols, and workflow orchestration  
automatically.  

## Core Components

**Agent**: An autonomous AI entity with a specific role and capabilities  
**Task**: A defined unit of work assigned to one or more agents  
**Crew**: A collection of agents working together on a common objective  
**Process**: The workflow that determines how tasks are executed  
**Tools**: External capabilities agents can use to complete tasks  

## Basic Agent Creation

The foundation of any CrewAI system starts with creating individual agents.  
Each agent needs a role, goal, backstory, and optionally tools to perform  
their designated functions.  

```python
from crewai import Agent, Task, Crew

agent = Agent(
    role="Research Assistant",
    goal="Find and summarize information on given topics",
    backstory="You are an experienced researcher with expertise in gathering "
              "and analyzing information from various sources.",
    verbose=True,
    allow_delegation=False
)

task = Task(
    description="Research the benefits of renewable energy",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

This creates a simple single-agent system where the research assistant  
performs information gathering tasks. The agent has clear boundaries  
defined by its role and goal, making it focused and effective.  

## Multiple Agents Collaboration

CrewAI's true power emerges when multiple agents collaborate on complex tasks.  
Different agents contribute their unique expertise to achieve better outcomes  
than any single agent could accomplish alone.  

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Research Analyst",
    goal="Gather comprehensive information on market trends",
    backstory="You are a skilled analyst with deep expertise in market research "
              "and data analysis.",
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging and informative articles",
    backstory="You are a professional writer with years of experience in "
              "creating compelling content for various audiences.",
    verbose=True
)

research_task = Task(
    description="Research current trends in artificial intelligence market",
    agent=researcher
)

writing_task = Task(
    description="Write a comprehensive article based on the research findings",
    agent=writer,
    context=[research_task]  # This task depends on research_task
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

The writing task explicitly depends on the research task through the context  
parameter, ensuring the writer has access to the researcher's findings  
before beginning their work.  

## Agent with Custom Tools

Agents become more powerful when equipped with specialized tools that extend  
their capabilities beyond text generation. Tools allow agents to interact  
with external systems, perform calculations, or access real-time data.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()

research_agent = Agent(
    role="Market Researcher",
    goal="Conduct thorough market analysis using web search",
    backstory="You are an expert market researcher with access to current "
              "web information and analytical capabilities.",
    tools=[search_tool],
    verbose=True
)

task = Task(
    description="Research the current state of electric vehicle adoption "
                "in European markets",
    agent=research_agent
)

crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

The SerperDevTool enables the agent to perform real-time web searches,  
significantly enhancing its research capabilities beyond its training data  
knowledge cutoff.  

## Sequential Task Processing

CrewAI supports different workflow patterns. Sequential processing ensures  
tasks execute in a specific order, with each task building upon previous  
results for complex, multi-stage operations.  

```python
from crewai import Agent, Task, Crew, Process

data_analyst = Agent(
    role="Data Analyst",
    goal="Analyze datasets and extract meaningful insights",
    backstory="You specialize in statistical analysis and data interpretation "
              "with strong attention to detail.",
    verbose=True
)

report_writer = Agent(
    role="Report Writer",
    goal="Transform data insights into clear, actionable reports",
    backstory="You excel at communicating complex data findings in "
              "accessible language for business stakeholders.",
    verbose=True
)

quality_reviewer = Agent(
    role="Quality Reviewer",
    goal="Review and improve the quality of reports",
    backstory="You have extensive experience in quality assurance and "
              "ensuring deliverables meet high standards.",
    verbose=True
)

analysis_task = Task(
    description="Analyze customer satisfaction survey data for Q3 2024",
    agent=data_analyst
)

report_task = Task(
    description="Create a comprehensive report based on the analysis",
    agent=report_writer
)

review_task = Task(
    description="Review the report for accuracy, clarity, and completeness",
    agent=quality_reviewer
)

crew = Crew(
    agents=[data_analyst, report_writer, quality_reviewer],
    tasks=[analysis_task, report_task, review_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
print(result)
```

Each agent performs their specialized task in sequence, with the output of  
one task serving as input for the next, creating a comprehensive workflow  
from raw data to finished report.  

## Hierarchical Task Management

For complex projects requiring supervision and coordination, CrewAI supports  
hierarchical processes where a manager agent oversees and delegates work  
to specialized team members.  

```python
from crewai import Agent, Task, Crew, Process

manager = Agent(
    role="Project Manager",
    goal="Coordinate team efforts and ensure project success",
    backstory="You are an experienced project manager with strong leadership "
              "and coordination skills across diverse teams.",
    verbose=True,
    allow_delegation=True
)

developer = Agent(
    role="Software Developer",
    goal="Write clean, efficient code based on requirements",
    backstory="You are a skilled developer with expertise in Python and "
              "software architecture principles.",
    verbose=True
)

tester = Agent(
    role="Quality Assurance Tester",
    goal="Test software thoroughly to identify bugs and issues",
    backstory="You specialize in comprehensive testing methodologies and "
              "have keen attention to detail.",
    verbose=True
)

project_task = Task(
    description="Develop a simple calculator application with comprehensive "
                "testing and documentation",
    agent=manager
)

crew = Crew(
    agents=[manager, developer, tester],
    tasks=[project_task],
    process=Process.hierarchical,
    manager_llm="gpt-4",  # Specify manager's LLM
    verbose=True
)

result = crew.kickoff()
print(result)
```

The manager agent delegates subtasks to appropriate team members and  
coordinates their efforts, simulating real-world project management  
dynamics in AI agent collaboration.  

## Custom Tool Creation

CrewAI allows you to create specialized tools tailored to your specific  
needs, enabling agents to perform domain-specific operations that aren't  
available in standard tool libraries.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
import requests

class WeatherTool(BaseTool):
    name: str = "Weather Information"
    description: str = "Get current weather information for any city"
    
    def _run(self, city: str) -> str:
        # Note: Replace with your actual weather API key
        api_key = "your_weather_api_key"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temp = round(data['main']['temp'] - 273.15, 1)  # Convert to Celsius
                description = data['weather'][0]['description']
                return f"Weather in {city}: {temp}°C, {description}"
            else:
                return f"Could not retrieve weather data for {city}"
        except Exception as e:
            return f"Error retrieving weather: {str(e)}"

weather_tool = WeatherTool()

travel_agent = Agent(
    role="Travel Advisor",
    goal="Provide helpful travel recommendations based on current conditions",
    backstory="You are an experienced travel advisor who helps people plan "
              "trips by considering weather and local conditions.",
    tools=[weather_tool],
    verbose=True
)

task = Task(
    description="Recommend the best European city to visit this weekend "
                "based on weather conditions",
    agent=travel_agent
)

crew = Crew(
    agents=[travel_agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Custom tools extend agent capabilities to interact with external APIs,  
databases, or perform specialized calculations specific to your application  
domain.  

## Memory and Context Sharing

CrewAI agents can maintain memory across interactions and share context  
between tasks, enabling more sophisticated reasoning and continuity in  
long-running processes.  

```python
from crewai import Agent, Task, Crew

sales_agent = Agent(
    role="Sales Representative",
    goal="Track customer interactions and identify sales opportunities",
    backstory="You are a seasoned sales professional with excellent "
              "relationship management and communication skills.",
    memory=True,  # Enable memory
    verbose=True
)

customer_service_agent = Agent(
    role="Customer Service Representative",
    goal="Provide excellent customer support and maintain satisfaction",
    backstory="You specialize in customer support with patience and "
              "problem-solving abilities.",
    memory=True,  # Enable memory
    verbose=True
)

initial_contact = Task(
    description="Handle initial customer inquiry about product pricing "
                "for John Smith from ABC Company",
    agent=sales_agent
)

follow_up = Task(
    description="Follow up on John Smith's pricing inquiry and address "
                "any concerns he might have",
    agent=customer_service_agent,
    context=[initial_contact]
)

crew = Crew(
    agents=[sales_agent, customer_service_agent],
    tasks=[initial_contact, follow_up],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Memory-enabled agents remember previous interactions, allowing for more  
personalized and contextually aware responses in subsequent conversations  
or related tasks.  

## Error Handling and Retry Logic

Robust CrewAI implementations include error handling and retry mechanisms  
to ensure reliability in production environments where external dependencies  
might occasionally fail.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import time

search_tool = SerperDevTool()

resilient_researcher = Agent(
    role="Resilient Researcher",
    goal="Conduct research with robust error handling",
    backstory="You are a thorough researcher who adapts to challenges and "
              "finds alternative approaches when initial methods fail.",
    tools=[search_tool],
    max_retry=3,  # Retry failed tasks up to 3 times
    verbose=True
)

def safe_task_execution(crew, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = crew.kickoff()
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All attempts failed")
                raise e

research_task = Task(
    description="Research emerging trends in quantum computing applications",
    agent=resilient_researcher
)

crew = Crew(
    agents=[resilient_researcher],
    tasks=[research_task],
    verbose=True
)

result = safe_task_execution(crew)
print(result)
```

This pattern ensures your multi-agent systems remain operational even when  
facing temporary network issues, API rate limits, or other transient  
failures.  

## Task Dependencies and Workflow Control

Complex workflows often require sophisticated task dependencies where  
certain tasks must complete before others can begin, creating intricate  
execution graphs.  

```python
from crewai import Agent, Task, Crew

requirements_analyst = Agent(
    role="Requirements Analyst",
    goal="Gather and analyze project requirements",
    backstory="You excel at understanding client needs and translating "
              "them into clear, actionable requirements.",
    verbose=True
)

architect = Agent(
    role="System Architect",
    goal="Design system architecture based on requirements",
    backstory="You have deep expertise in system design and architectural "
              "patterns for scalable applications.",
    verbose=True
)

frontend_dev = Agent(
    role="Frontend Developer",
    goal="Implement user interface based on architectural specifications",
    backstory="You specialize in creating intuitive, responsive user "
              "interfaces using modern web technologies.",
    verbose=True
)

backend_dev = Agent(
    role="Backend Developer",
    goal="Implement server-side logic and database design",
    backstory="You are expert in server-side development, API design, "
              "and database optimization.",
    verbose=True
)

# Independent initial task
requirements_task = Task(
    description="Analyze requirements for an e-commerce platform",
    agent=requirements_analyst
)

# Depends on requirements
architecture_task = Task(
    description="Design system architecture for the e-commerce platform",
    agent=architect,
    context=[requirements_task]
)

# Both depend on architecture
frontend_task = Task(
    description="Develop the user interface based on architecture",
    agent=frontend_dev,
    context=[architecture_task]
)

backend_task = Task(
    description="Implement backend services based on architecture",
    agent=backend_dev,
    context=[architecture_task]
)

crew = Crew(
    agents=[requirements_analyst, architect, frontend_dev, backend_dev],
    tasks=[requirements_task, architecture_task, frontend_task, backend_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Task dependencies ensure logical execution order while allowing parallel  
execution where possible, optimizing overall workflow efficiency.  

## Agent Specialization with Domain Knowledge

Specialized agents with domain-specific knowledge and prompting can deliver  
higher quality results in their areas of expertise compared to generalist  
approaches.  

```python
from crewai import Agent, Task, Crew

medical_researcher = Agent(
    role="Medical Research Specialist",
    goal="Analyze medical literature and provide evidence-based insights",
    backstory="You are a medical researcher with PhD in biomedical sciences "
              "and extensive experience in clinical research methodologies. "
              "You always cite sources and consider ethical implications.",
    verbose=True,
    max_execution_time=300  # 5 minutes timeout
)

health_writer = Agent(
    role="Health Content Writer",
    goal="Transform medical research into accessible health information",
    backstory="You specialize in medical writing with ability to explain "
              "complex health topics in clear, accurate language for "
              "general audiences without losing scientific accuracy.",
    verbose=True
)

fact_checker = Agent(
    role="Medical Fact Checker",
    goal="Verify accuracy and safety of health-related content",
    backstory="You are a medical professional focused on ensuring health "
              "information is accurate, up-to-date, and safe for public "
              "consumption.",
    verbose=True
)

research_task = Task(
    description="Research the latest findings on the Mediterranean diet's "
                "impact on cardiovascular health",
    agent=medical_researcher
)

writing_task = Task(
    description="Write a patient-friendly article about Mediterranean diet "
                "benefits for heart health",
    agent=health_writer,
    context=[research_task]
)

verification_task = Task(
    description="Review the article for medical accuracy and safety",
    agent=fact_checker,
    context=[writing_task]
)

crew = Crew(
    agents=[medical_researcher, health_writer, fact_checker],
    tasks=[research_task, writing_task, verification_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Domain-specialized agents leverage detailed backstories and role definitions  
to provide expert-level analysis and content creation within their fields  
of expertise.  

## Dynamic Task Generation

Advanced CrewAI systems can generate new tasks dynamically based on  
intermediate results, allowing for adaptive workflows that respond to  
discovered information or changing requirements.  

```python
from crewai import Agent, Task, Crew

coordinator = Agent(
    role="Project Coordinator",
    goal="Manage dynamic project workflows and task generation",
    backstory="You excel at project coordination and can adapt workflows "
              "based on evolving requirements and discovered information.",
    verbose=True,
    allow_delegation=True
)

investigator = Agent(
    role="Business Investigator",
    goal="Investigate business opportunities and gather intelligence",
    backstory="You are skilled at business analysis and competitive "
              "intelligence gathering.",
    verbose=True
)

analyst = Agent(
    role="Market Analyst",
    goal="Analyze market data and provide strategic insights",
    backstory="You specialize in market analysis and strategic planning "
              "with strong analytical capabilities.",
    verbose=True
)

def create_follow_up_tasks(initial_result):
    """Generate additional tasks based on initial findings"""
    tasks = []
    
    if "competitor" in initial_result.lower():
        tasks.append(Task(
            description="Conduct detailed competitive analysis of identified competitors",
            agent=analyst
        ))
    
    if "opportunity" in initial_result.lower():
        tasks.append(Task(
            description="Develop strategy recommendations for identified opportunities",
            agent=analyst
        ))
    
    return tasks

initial_investigation = Task(
    description="Investigate market opportunities in renewable energy sector",
    agent=investigator
)

crew = Crew(
    agents=[coordinator, investigator, analyst],
    tasks=[initial_investigation],
    verbose=True
)

# Execute initial phase
initial_result = crew.kickoff()

# Generate and execute follow-up tasks based on results
follow_up_tasks = create_follow_up_tasks(str(initial_result))

if follow_up_tasks:
    follow_up_crew = Crew(
        agents=[analyst],
        tasks=follow_up_tasks,
        verbose=True
    )
    
    final_result = follow_up_crew.kickoff()
    print("Initial Result:", initial_result)
    print("Follow-up Results:", final_result)
else:
    print("Final Result:", initial_result)
```

Dynamic task generation enables responsive workflows that adapt to discovered  
information, ensuring comprehensive coverage of complex, evolving projects.  

## Multi-Language Support

CrewAI agents can be configured to work in different languages, enabling  
global applications and multilingual content generation workflows.  

```python
from crewai import Agent, Task, Crew

translator = Agent(
    role="Professional Translator",
    goal="Provide accurate translations while preserving meaning and context",
    backstory="You are a certified translator with expertise in multiple "
              "languages and cultural nuances. You maintain accuracy while "
              "adapting content appropriately for target audiences.",
    verbose=True
)

cultural_advisor = Agent(
    role="Cultural Adaptation Specialist",
    goal="Ensure content is culturally appropriate for target markets",
    backstory="You specialize in cultural adaptation and localization, "
              "ensuring content resonates with local audiences while "
              "respecting cultural sensitivities.",
    verbose=True
)

content_reviewer = Agent(
    role="Multilingual Content Reviewer",
    goal="Review translated content for quality and consistency",
    backstory="You review multilingual content with native-level fluency "
              "in multiple languages and strong editorial skills.",
    verbose=True
)

translation_task = Task(
    description="Translate this marketing message to German: "
                "'Hello there! Discover our innovative solutions that "
                "transform businesses worldwide.'",
    agent=translator
)

cultural_task = Task(
    description="Adapt the translated content for German business culture",
    agent=cultural_advisor,
    context=[translation_task]
)

review_task = Task(
    description="Review the culturally adapted German content for accuracy",
    agent=content_reviewer,
    context=[cultural_task]
)

crew = Crew(
    agents=[translator, cultural_advisor, content_reviewer],
    tasks=[translation_task, cultural_task, review_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Multilingual workflows ensure content quality across language barriers  
while maintaining cultural sensitivity and market appropriateness.  

## Agent Performance Monitoring

Monitoring agent performance and task execution helps optimize workflows  
and identify areas for improvement in complex multi-agent systems.  

```python
from crewai import Agent, Task, Crew
import time
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    def start_task(self, task_id):
        self.metrics[task_id] = {
            'start_time': time.time(),
            'start_datetime': datetime.now()
        }
    
    def end_task(self, task_id, success=True):
        if task_id in self.metrics:
            self.metrics[task_id]['end_time'] = time.time()
            self.metrics[task_id]['duration'] = (
                self.metrics[task_id]['end_time'] - 
                self.metrics[task_id]['start_time']
            )
            self.metrics[task_id]['success'] = success
    
    def get_report(self):
        report = "Performance Report:\n"
        for task_id, data in self.metrics.items():
            status = "✓" if data.get('success', False) else "✗"
            duration = data.get('duration', 0)
            report += f"{status} {task_id}: {duration:.2f}s\n"
        return report

monitor = PerformanceMonitor()

performance_analyst = Agent(
    role="Performance Analyst",
    goal="Analyze system performance and provide optimization recommendations",
    backstory="You specialize in performance analysis and system optimization "
              "with strong analytical and troubleshooting skills.",
    verbose=True
)

data_processor = Agent(
    role="Data Processor",
    goal="Process and analyze large datasets efficiently",
    backstory="You excel at data processing and can handle large volumes "
              "of information with attention to accuracy and speed.",
    verbose=True
)

# Simulate monitored task execution
task1 = Task(
    description="Analyze performance metrics for Q4 2024",
    agent=performance_analyst
)

task2 = Task(
    description="Process customer data for performance analysis",
    agent=data_processor
)

crew = Crew(
    agents=[performance_analyst, data_processor],
    tasks=[task1, task2],
    verbose=True
)

# Monitor execution
monitor.start_task("performance_analysis")
try:
    result = crew.kickoff()
    monitor.end_task("performance_analysis", success=True)
except Exception as e:
    monitor.end_task("performance_analysis", success=False)
    print(f"Task failed: {e}")

print(monitor.get_report())
print("Results:", result)
```

Performance monitoring provides insights into agent efficiency and helps  
identify bottlenecks or optimization opportunities in complex workflows.  

## Integration with External APIs

CrewAI agents can integrate with various external APIs and services,  
extending their capabilities beyond text generation to interact with  
real-world systems and data sources.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
import requests
import json

class CRMTool(BaseTool):
    name: str = "CRM Integration"
    description: str = "Access customer relationship management system"
    
    def _run(self, action: str, customer_id: str = None) -> str:
        # Mock CRM API integration
        if action == "get_customer":
            return json.dumps({
                "customer_id": customer_id,
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "last_purchase": "2024-01-15",
                "total_value": "$2,450"
            })
        elif action == "list_customers":
            return json.dumps([
                {"id": "001", "name": "Jane Smith", "status": "active"},
                {"id": "002", "name": "Bob Johnson", "status": "inactive"}
            ])
        else:
            return "Invalid action"

class EmailTool(BaseTool):
    name: str = "Email System"
    description: str = "Send automated emails to customers"
    
    def _run(self, recipient: str, subject: str, body: str) -> str:
        # Mock email sending
        return f"Email sent to {recipient} with subject: {subject}"

crm_tool = CRMTool()
email_tool = EmailTool()

customer_service_manager = Agent(
    role="Customer Service Manager",
    goal="Manage customer relationships and communication",
    backstory="You excel at customer relationship management with access "
              "to customer data and communication tools.",
    tools=[crm_tool, email_tool],
    verbose=True
)

outreach_task = Task(
    description="Review inactive customers and send personalized re-engagement emails",
    agent=customer_service_manager
)

crew = Crew(
    agents=[customer_service_manager],
    tasks=[outreach_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

API integration enables agents to perform real-world actions like updating  
databases, sending communications, or retrieving live data from external  
systems.  

## Collaborative Decision Making

Multiple agents can collaborate on complex decisions by contributing  
different perspectives and expertise, resulting in more comprehensive  
and well-reasoned outcomes.  

```python
from crewai import Agent, Task, Crew

financial_analyst = Agent(
    role="Financial Analyst",
    goal="Analyze financial implications and provide cost-benefit analysis",
    backstory="You are expert in financial analysis with strong skills in "
              "budgeting, forecasting, and risk assessment.",
    verbose=True
)

technical_architect = Agent(
    role="Technical Architect",
    goal="Evaluate technical feasibility and implementation complexity",
    backstory="You have deep technical expertise and experience in system "
              "architecture, technology evaluation, and implementation planning.",
    verbose=True
)

risk_manager = Agent(
    role="Risk Manager",
    goal="Identify and assess potential risks and mitigation strategies",
    backstory="You specialize in risk management with expertise in identifying "
              "potential issues and developing risk mitigation strategies.",
    verbose=True
)

decision_coordinator = Agent(
    role="Decision Coordinator",
    goal="Synthesize input from all stakeholders and recommend final decision",
    backstory="You excel at collaborative decision-making and can weigh "
              "multiple perspectives to reach optimal conclusions.",
    verbose=True,
    allow_delegation=True
)

financial_analysis = Task(
    description="Analyze the financial impact of implementing a new CRM system "
                "with $50,000 budget allocation",
    agent=financial_analyst
)

technical_evaluation = Task(
    description="Evaluate technical requirements and implementation complexity "
                "for the CRM system",
    agent=technical_architect
)

risk_assessment = Task(
    description="Identify potential risks and challenges in CRM implementation",
    agent=risk_manager
)

final_decision = Task(
    description="Based on financial, technical, and risk analyses, make "
                "a recommendation on whether to proceed with CRM implementation",
    agent=decision_coordinator,
    context=[financial_analysis, technical_evaluation, risk_assessment]
)

crew = Crew(
    agents=[financial_analyst, technical_architect, risk_manager, decision_coordinator],
    tasks=[financial_analysis, technical_evaluation, risk_assessment, final_decision],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Collaborative decision-making leverages diverse expertise to make more  
informed choices than any single agent could achieve independently.  

## Agent Learning and Adaptation

Agents can learn from previous interactions and adapt their behavior  
based on feedback, improving performance over time in recurring scenarios.  

```python
from crewai import Agent, Task, Crew
import json
import os

class LearningAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.knowledge_file = f"{self.role.lower().replace(' ', '_')}_knowledge.json"
        self.load_knowledge()
    
    def load_knowledge(self):
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r') as f:
                self.learned_knowledge = json.load(f)
        else:
            self.learned_knowledge = {}
    
    def save_knowledge(self, key, value):
        self.learned_knowledge[key] = value
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.learned_knowledge, f, indent=2)
    
    def get_knowledge(self, key):
        return self.learned_knowledge.get(key, None)

adaptive_consultant = LearningAgent(
    role="Business Consultant",
    goal="Provide increasingly better business advice through learning",
    backstory="You are a business consultant who learns from each engagement "
              "and improves recommendations based on past experiences.",
    verbose=True
)

def consultation_with_feedback(consultant, client_query, feedback=None):
    # Check for relevant past knowledge
    similar_knowledge = consultant.get_knowledge("similar_queries")
    
    enhanced_backstory = consultant.backstory
    if similar_knowledge:
        enhanced_backstory += f" Based on past experiences: {similar_knowledge}"
    
    task = Task(
        description=f"Provide business consulting advice for: {client_query}",
        agent=consultant
    )
    
    crew = Crew(
        agents=[consultant],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    # Store learning from feedback
    if feedback:
        consultant.save_knowledge(
            f"query_{len(consultant.learned_knowledge)}",
            {
                "query": client_query,
                "result": str(result),
                "feedback": feedback
            }
        )
    
    return result

# First consultation
query1 = "How can I improve team productivity?"
result1 = consultation_with_feedback(adaptive_consultant, query1)
print("First consultation result:", result1)

# Provide feedback for learning
feedback1 = "The advice was helpful but could include more specific metrics"
consultation_with_feedback(adaptive_consultant, query1, feedback1)

# Second consultation on similar topic
query2 = "What metrics should I track for team productivity?"
result2 = consultation_with_feedback(adaptive_consultant, query2)
print("Second consultation result:", result2)
```

Learning agents build institutional knowledge over time, becoming more  
effective as they accumulate experience and feedback from their interactions.  

## Real-Time Data Processing

CrewAI can handle real-time data streams and dynamic content generation,  
making it suitable for applications requiring immediate responses to  
changing conditions.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
import time
import random
from datetime import datetime

class LiveDataTool(BaseTool):
    name: str = "Live Data Monitor"
    description: str = "Monitor real-time data streams and metrics"
    
    def _run(self, data_type: str) -> str:
        # Simulate real-time data
        if data_type == "stock":
            price = round(random.uniform(100, 200), 2)
            change = round(random.uniform(-5, 5), 2)
            return f"AAPL: ${price} ({change:+.2f})"
        elif data_type == "server":
            cpu = random.randint(20, 80)
            memory = random.randint(30, 90)
            return f"Server: CPU {cpu}%, Memory {memory}%"
        else:
            return f"Unknown data type: {data_type}"

live_data_tool = LiveDataTool()

monitoring_agent = Agent(
    role="Real-Time Monitor",
    goal="Monitor live data and provide instant analysis",
    backstory="You specialize in real-time monitoring and can quickly "
              "analyze changing conditions to provide timely insights.",
    tools=[live_data_tool],
    verbose=True
)

alert_agent = Agent(
    role="Alert Manager",
    goal="Generate appropriate alerts based on monitoring data",
    backstory="You excel at determining when conditions warrant alerts "
              "and crafting appropriate notifications for different audiences.",
    verbose=True
)

def real_time_monitoring_cycle():
    monitoring_task = Task(
        description="Monitor current stock prices and server performance metrics",
        agent=monitoring_agent
    )
    
    analysis_task = Task(
        description="Analyze the monitoring data and determine if any alerts are needed",
        agent=alert_agent,
        context=[monitoring_task]
    )
    
    crew = Crew(
        agents=[monitoring_agent, alert_agent],
        tasks=[monitoring_task, analysis_task],
        verbose=True
    )
    
    return crew.kickoff()

# Simulate real-time monitoring
print("Starting real-time monitoring simulation...")
for i in range(3):
    print(f"\n--- Monitoring Cycle {i+1} at {datetime.now()} ---")
    result = real_time_monitoring_cycle()
    print("Cycle result:", result)
    time.sleep(2)  # Wait before next cycle

print("\nMonitoring simulation complete")
```

Real-time processing enables CrewAI systems to respond immediately to  
changing conditions, making them suitable for monitoring, alerting,  
and dynamic response applications.  

## Content Generation Pipeline

CrewAI excels at content creation workflows involving multiple stages  
of refinement, review, and optimization for different audiences and  
platforms.  

```python
from crewai import Agent, Task, Crew

content_strategist = Agent(
    role="Content Strategist",
    goal="Develop comprehensive content strategies and messaging frameworks",
    backstory="You have extensive experience in content marketing with deep "
              "understanding of audience psychology and engagement strategies.",
    verbose=True
)

copywriter = Agent(
    role="Creative Copywriter",
    goal="Write compelling, engaging copy that resonates with target audiences",
    backstory="You are a creative writer with talent for crafting memorable "
              "copy that drives action and builds brand connection.",
    verbose=True
)

seo_specialist = Agent(
    role="SEO Specialist",
    goal="Optimize content for search engines and online discoverability",
    backstory="You specialize in SEO with deep knowledge of search algorithms "
              "and optimization techniques for improved visibility.",
    verbose=True
)

editor = Agent(
    role="Content Editor",
    goal="Refine and polish content for clarity, accuracy, and impact",
    backstory="You are an experienced editor with keen eye for detail and "
              "expertise in improving content quality and readability.",
    verbose=True
)

strategy_task = Task(
    description="Develop a content strategy for launching a sustainable "
                "fashion brand targeting environmentally conscious millennials",
    agent=content_strategist
)

writing_task = Task(
    description="Write blog post content based on the strategy",
    agent=copywriter,
    context=[strategy_task]
)

seo_task = Task(
    description="Optimize the blog post for SEO and search visibility",
    agent=seo_specialist,
    context=[writing_task]
)

editing_task = Task(
    description="Edit and finalize the SEO-optimized content",
    agent=editor,
    context=[seo_task]
)

crew = Crew(
    agents=[content_strategist, copywriter, seo_specialist, editor],
    tasks=[strategy_task, writing_task, seo_task, editing_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

Content pipelines leverage specialized expertise at each stage to create  
high-quality, optimized content that meets multiple objectives simultaneously.  

## Advanced Workflow Orchestration

Complex business processes can be modeled using sophisticated workflow  
patterns that handle branching logic, conditional execution, and parallel  
processing streams.  

```python
from crewai import Agent, Task, Crew
from crewai_tools import BaseTool

class WorkflowController(BaseTool):
    name: str = "Workflow Controller"
    description: str = "Control workflow execution based on conditions"
    
    def _run(self, condition: str, value: str) -> str:
        if condition == "budget_check":
            budget = float(value)
            if budget > 10000:
                return "high_budget_workflow"
            elif budget > 5000:
                return "medium_budget_workflow"
            else:
                return "low_budget_workflow"
        return "standard_workflow"

workflow_tool = WorkflowController()

workflow_manager = Agent(
    role="Workflow Manager",
    goal="Orchestrate complex business workflows based on conditions",
    backstory="You excel at workflow management and can dynamically route "
              "processes based on various business conditions and requirements.",
    tools=[workflow_tool],
    verbose=True
)

budget_analyst = Agent(
    role="Budget Analyst",
    goal="Analyze project budgets and financial constraints",
    backstory="You specialize in financial analysis and budget planning "
              "with strong attention to cost optimization.",
    verbose=True
)

project_manager = Agent(
    role="Project Manager",
    goal="Execute projects according to assigned workflow type",
    backstory="You are experienced in managing projects of various scales "
              "and complexities with adaptability to different approaches.",
    verbose=True
)

senior_director = Agent(
    role="Senior Director",
    goal="Provide executive oversight for high-value projects",
    backstory="You provide strategic leadership and executive oversight "
              "for major initiatives and high-budget projects.",
    verbose=True
)

def execute_conditional_workflow(project_description, budget):
    # Initial workflow routing
    routing_task = Task(
        description=f"Determine appropriate workflow for project with budget ${budget}: {project_description}",
        agent=workflow_manager
    )
    
    budget_task = Task(
        description=f"Analyze budget allocation for ${budget} project budget",
        agent=budget_analyst
    )
    
    initial_crew = Crew(
        agents=[workflow_manager, budget_analyst],
        tasks=[routing_task, budget_task],
        verbose=True
    )
    
    initial_result = initial_crew.kickoff()
    
    # Execute appropriate workflow based on routing
    if budget > 10000:
        # High-budget workflow requires executive approval
        exec_task = Task(
            description=f"Review and approve high-budget project: {project_description}",
            agent=senior_director
        )
        
        exec_crew = Crew(
            agents=[senior_director],
            tasks=[exec_task],
            verbose=True
        )
        
        exec_result = exec_crew.kickoff()
        return f"Initial Analysis: {initial_result}\nExecutive Review: {exec_result}"
    
    else:
        # Standard workflow
        project_task = Task(
            description=f"Execute project according to standard workflow: {project_description}",
            agent=project_manager
        )
        
        project_crew = Crew(
            agents=[project_manager],
            tasks=[project_task],
            verbose=True
        )
        
        project_result = project_crew.kickoff()
        return f"Initial Analysis: {initial_result}\nProject Execution: {project_result}"

# Test different workflow paths
low_budget_result = execute_conditional_workflow(
    "Develop company newsletter template", 3000
)

high_budget_result = execute_conditional_workflow(
    "Implement enterprise CRM system", 15000
)

print("Low Budget Workflow Result:", low_budget_result)
print("\nHigh Budget Workflow Result:", high_budget_result)
```

Advanced orchestration enables dynamic workflow adaptation based on business  
rules, ensuring appropriate processes are followed for different scenarios  
and requirements.  

## Integration Testing and Validation

Comprehensive testing ensures CrewAI systems perform reliably across  
different scenarios and edge cases, maintaining quality in production  
environments.  

```python
from crewai import Agent, Task, Crew
import unittest
from unittest.mock import patch

class CrewAITestSuite:
    def __init__(self):
        self.test_results = []
    
    def create_test_agents(self):
        validator = Agent(
            role="Quality Validator",
            goal="Validate outputs meet quality standards",
            backstory="You are meticulous in testing and validation with "
                      "strong attention to detail and quality standards.",
            verbose=False  # Reduce noise during testing
        )
        
        analyzer = Agent(
            role="Test Analyzer",
            goal="Analyze test results and identify issues",
            backstory="You excel at analyzing test outcomes and identifying "
                      "patterns or issues that need attention.",
            verbose=False
        )
        
        return validator, analyzer
    
    def test_basic_functionality(self):
        validator, analyzer = self.create_test_agents()
        
        test_task = Task(
            description="Validate that basic agent communication works correctly",
            agent=validator
        )
        
        analysis_task = Task(
            description="Analyze the validation results for any issues",
            agent=analyzer,
            context=[test_task]
        )
        
        crew = Crew(
            agents=[validator, analyzer],
            tasks=[test_task, analysis_task],
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            self.test_results.append({
                "test": "basic_functionality",
                "status": "passed",
                "result": str(result)
            })
            return True
        except Exception as e:
            self.test_results.append({
                "test": "basic_functionality",
                "status": "failed",
                "error": str(e)
            })
            return False
    
    def test_error_handling(self):
        validator, analyzer = self.create_test_agents()
        
        # Intentionally create a problematic task
        error_task = Task(
            description="This task should handle errors gracefully: " + "x" * 10000,
            agent=validator
        )
        
        crew = Crew(
            agents=[validator],
            tasks=[error_task],
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            self.test_results.append({
                "test": "error_handling",
                "status": "passed",
                "result": "Error handled gracefully"
            })
            return True
        except Exception as e:
            # Expected behavior for this test
            self.test_results.append({
                "test": "error_handling",
                "status": "passed",
                "result": f"Error properly caught: {str(e)[:100]}"
            })
            return True
    
    def test_multi_agent_coordination(self):
        validator, analyzer = self.create_test_agents()
        
        coordinator = Agent(
            role="Test Coordinator",
            goal="Coordinate multi-agent testing scenarios",
            backstory="You excel at coordinating multiple agents and ensuring "
                      "proper communication flow.",
            verbose=False
        )
        
        coord_task = Task(
            description="Coordinate a multi-agent test scenario",
            agent=coordinator
        )
        
        validation_task = Task(
            description="Validate coordination effectiveness",
            agent=validator,
            context=[coord_task]
        )
        
        crew = Crew(
            agents=[coordinator, validator],
            tasks=[coord_task, validation_task],
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            self.test_results.append({
                "test": "multi_agent_coordination",
                "status": "passed",
                "result": "Multi-agent coordination successful"
            })
            return True
        except Exception as e:
            self.test_results.append({
                "test": "multi_agent_coordination",
                "status": "failed",
                "error": str(e)
            })
            return False
    
    def run_all_tests(self):
        print("Running CrewAI Test Suite...")
        
        tests = [
            self.test_basic_functionality,
            self.test_error_handling,
            self.test_multi_agent_coordination
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        print(f"\nTest Results: {passed}/{len(tests)} tests passed")
        
        for result in self.test_results:
            status_symbol = "✓" if result["status"] == "passed" else "✗"
            print(f"{status_symbol} {result['test']}: {result.get('result', result.get('error', ''))}")
        
        return passed == len(tests)

# Run the test suite
test_suite = CrewAITestSuite()
all_tests_passed = test_suite.run_all_tests()

if all_tests_passed:
    print("\n🎉 All tests passed! CrewAI system is functioning correctly.")
else:
    print("\n⚠️ Some tests failed. Review the results above for details.")
```

Comprehensive testing validates system reliability and helps identify  
potential issues before deployment, ensuring robust performance in  
production environments.  

## Production Deployment Patterns

CrewAI systems require careful consideration for production deployment,  
including configuration management, scaling strategies, and monitoring  
infrastructure.  

```python
from crewai import Agent, Task, Crew
import os
import logging
from datetime import datetime
import json

# Production configuration
class ProductionConfig:
    def __init__(self):
        self.llm_model = os.getenv("CREWAI_MODEL", "gpt-4")
        self.max_execution_time = int(os.getenv("MAX_EXECUTION_TIME", "600"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.enable_memory = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
        
    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crewai_production.log'),
                logging.StreamHandler()
            ]
        )

class ProductionCrewManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_duration": 0
        }
    
    def create_production_agents(self):
        # Production-ready agents with proper error handling
        primary_agent = Agent(
            role="Production Assistant",
            goal="Handle production workloads reliably and efficiently",
            backstory="You are a production-ready assistant optimized for "
                      "reliability, efficiency, and consistent performance.",
            memory=self.config.enable_memory,
            max_execution_time=self.config.max_execution_time,
            verbose=True
        )
        
        backup_agent = Agent(
            role="Backup Assistant",
            goal="Provide redundancy and backup processing capabilities",
            backstory="You serve as backup support to ensure continued "
                      "operation when primary systems encounter issues.",
            memory=self.config.enable_memory,
            max_execution_time=self.config.max_execution_time,
            verbose=True
        )
        
        return primary_agent, backup_agent
    
    def execute_with_fallback(self, task_description):
        start_time = datetime.now()
        self.metrics["total_executions"] += 1
        
        try:
            primary_agent, backup_agent = self.create_production_agents()
            
            # Primary execution attempt
            primary_task = Task(
                description=task_description,
                agent=primary_agent
            )
            
            crew = Crew(
                agents=[primary_agent],
                tasks=[primary_task],
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Log success
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Task completed successfully in {duration:.2f}s")
            self.metrics["successful_executions"] += 1
            self.update_average_duration(duration)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": duration,
                "agent": "primary"
            }
            
        except Exception as primary_error:
            self.logger.warning(f"Primary execution failed: {primary_error}")
            
            try:
                # Fallback to backup agent
                self.logger.info("Attempting fallback execution...")
                
                backup_task = Task(
                    description=f"Fallback execution: {task_description}",
                    agent=backup_agent
                )
                
                backup_crew = Crew(
                    agents=[backup_agent],
                    tasks=[backup_task],
                    verbose=True
                )
                
                result = backup_crew.kickoff()
                
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.info(f"Fallback completed successfully in {duration:.2f}s")
                self.metrics["successful_executions"] += 1
                self.update_average_duration(duration)
                
                return {
                    "status": "success_fallback",
                    "result": result,
                    "execution_time": duration,
                    "agent": "backup",
                    "primary_error": str(primary_error)
                }
                
            except Exception as backup_error:
                # Both attempts failed
                duration = (datetime.now() - start_time).total_seconds()
                self.logger.error(f"Both primary and backup execution failed")
                self.metrics["failed_executions"] += 1
                
                return {
                    "status": "failed",
                    "primary_error": str(primary_error),
                    "backup_error": str(backup_error),
                    "execution_time": duration
                }
    
    def update_average_duration(self, duration):
        current_avg = self.metrics["average_duration"]
        success_count = self.metrics["successful_executions"]
        
        if success_count == 1:
            self.metrics["average_duration"] = duration
        else:
            # Update running average
            self.metrics["average_duration"] = (
                (current_avg * (success_count - 1) + duration) / success_count
            )
    
    def get_health_status(self):
        total = self.metrics["total_executions"]
        if total == 0:
            return {"status": "ready", "metrics": self.metrics}
        
        success_rate = (self.metrics["successful_executions"] / total) * 100
        
        if success_rate >= 95:
            status = "healthy"
        elif success_rate >= 80:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "success_rate": f"{success_rate:.1f}%",
            "metrics": self.metrics
        }

# Production deployment example
def deploy_production_system():
    config = ProductionConfig()
    config.setup_logging()
    
    crew_manager = ProductionCrewManager(config)
    
    # Simulate production workload
    test_tasks = [
        "Analyze quarterly sales performance and generate insights",
        "Process customer feedback and identify improvement areas",
        "Generate weekly status report for management team"
    ]
    
    print("🚀 Starting production deployment...")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n📋 Executing production task {i}/{len(test_tasks)}")
        result = crew_manager.execute_with_fallback(task)
        
        print(f"Status: {result['status']}")
        print(f"Duration: {result['execution_time']:.2f}s")
        
        if result['status'] == 'failed':
            print(f"⚠️ Task failed: {result}")
    
    # Health check
    health = crew_manager.get_health_status()
    print(f"\n📊 System Health: {health['status']}")
    print(f"Success Rate: {health['success_rate']}")
    print(f"Average Duration: {health['metrics']['average_duration']:.2f}s")
    
    return crew_manager

# Deploy the system
production_manager = deploy_production_system()
```

Production deployment patterns ensure CrewAI systems operate reliably  
at scale with proper monitoring, fallback mechanisms, and performance  
tracking for enterprise environments.  