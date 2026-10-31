from agents import Agent
from ghost_projects.ai.prompts import SYSTEM_PROMPT
from ghost_projects.schemas.assessment import ProjectAssessment

def create_investigation_agent(model, tools):
    """
    Creates and configures the Ghost Projects Archaeologist agent.
    
    Args:
        model: The configured model provider (OpenAIChatCompletionsModel).
        tools: A list of SDK-compatible function-tool objects.
        
    Returns:
        A configured Agent instance.
    """
    return Agent(
        name="Projects Archaeologist",
        instructions=SYSTEM_PROMPT,
        model=model,
        tools=tools,
        # Configure structured output to match the ProjectAssessment model
        # output_type=ProjectAssessment,
    )