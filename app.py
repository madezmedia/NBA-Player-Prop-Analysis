import streamlit as st
import os
import json
import requests
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional

# Advanced AI and Web Integration
from groq import Groq
from crewai import Agent, Task, Crew
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

# Data Processing and Validation
import pandas as pd
import numpy as np
from utils.data_validation import BasketballDataValidator
from utils.api_integration import BasketballAPIIntegration
from utils.feature_engineering import BasketballFeatureEngineer
from utils.error_handler import ErrorHandler

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Advanced Basketball AI Analyst",
    page_icon="🏀",
    layout="wide"
)

class AdvancedBasketballAnalyst:
    def __init__(self):
        """
        Initialize the basketball analyst with advanced AI and data processing capabilities
        """
        # Initialize error handling
        self.error_handler = ErrorHandler()
        
        # Initialize API clients with error handling
        self.groq_client = self.error_handler.safe_execute(
            Groq, 
            default_return=None, 
            api_key=os.getenv('GROQ_API_KEY')
        )
        
        # Fallback to None if OpenAI API key is not set
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_client = self.error_handler.safe_execute(
            ChatOpenAI, 
            default_return=None,
            api_key=openai_api_key,
            model="gpt-4o-mini"  # Use GPT-4o mini model
        ) if openai_api_key else None
        
        # Initialize utility classes
        self.data_validator = BasketballDataValidator()
        self.api_integration = BasketballAPIIntegration()
        self.feature_engineer = BasketballFeatureEngineer()
    
    def create_web_browsing_tool(self) -> Tool:
        """
        Create a web browsing tool for gathering real-time information
        """
        async def async_web_search(query: str, max_chars: int = 5000) -> str:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://duckduckgo.com/html/?q={query}") as response:
                    content = await response.text()
                    # Truncate content to manage token usage
                    return content[:max_chars]
        
        def web_search(query: str) -> str:
            return asyncio.run(async_web_search(query))
        
        return Tool(
            name="Web Search",
            func=web_search,
            description="Perform web searches to gather real-time information with content truncation"
        )
    
    def generate_comprehensive_analysis(
        self, 
        player_name: str, 
        include_web_research: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive player performance analysis
        
        :param player_name: Name of the player to analyze
        :param include_web_research: Whether to include web research context
        :return: Comprehensive analysis dictionary
        """
        try:
            # Determine which client to use
            if self.groq_client:
                client = self.groq_client
                model = "llama3-70b-8192"
            elif self.openai_client:
                client = self.openai_client
                model = "gpt-4o-mini"
            else:
                return {
                    "error": "No AI client available. Check API configurations."
                }
            
            # Prepare base query
            base_query = f"""
            Provide a comprehensive, multi-dimensional analysis of {player_name}'s basketball career:

            1. Career Overview:
            - Early life and basketball journey
            - Draft details and initial NBA years
            - Team history and transitions

            2. Statistical Achievements:
            - Career points, assists, rebounds
            - Shooting percentages
            - Notable records and milestones

            3. Performance Analysis:
            - Strengths and playing style
            - Impact on team dynamics
            - Comparative performance against peers

            4. Awards and Recognitions:
            - MVP awards
            - All-Star selections
            - Championship contributions

            5. Future Potential:
            - Career trajectory
            - Potential future achievements
            """
            
            # Add web research if enabled
            if include_web_research:
                web_context = self.create_web_browsing_tool().run(f"{player_name} basketball career highlights")
                base_query += f"\n\nAdditional Context from Web Research:\n{web_context}"
            
            # Use appropriate method based on client
            if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
                # Groq-style invocation
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an advanced basketball performance analyst."},
                        {"role": "user", "content": base_query}
                    ]
                )
                analysis_content = response.choices[0].message.content
            else:
                # OpenAI/Langchain-style invocation
                response = client.invoke(base_query)
                analysis_content = response.content
            
            return {
                "player": player_name,
                "analysis": analysis_content,
                "timestamp": datetime.now().isoformat(),
                "source": "Groq" if client == self.groq_client else "OpenAI"
            }
        
        except Exception as e:
            return {
                "player": player_name,
                "error": f"Analysis generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def advanced_function_calling_analysis(
        self, 
        query: str
    ) -> Dict[str, Any]:
        """
        Advanced function calling analysis with multiple tool integrations
        
        :param query: User's query for basketball analysis
        :return: Analysis result with function calls
        """
        try:
            # Determine which client to use
            if self.groq_client:
                client = self.groq_client
                model = "llama3-70b-8192"
            elif self.openai_client:
                client = self.openai_client
                model = "gpt-4o-mini"
            else:
                return {
                    "error": "No AI client available. Check API configurations."
                }
            
            # Use appropriate method based on client
            if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
                # Groq-style invocation
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an advanced basketball performance analyst."},
                        {"role": "user", "content": query}
                    ]
                )
                response_content = response.choices[0].message.content
            else:
                # OpenAI/Langchain-style invocation
                response = client.invoke(query)
                response_content = response.content
            
            return {
                "response": response_content,
                "source": "Groq" if client == self.groq_client else "OpenAI"
            }
        
        except Exception as e:
            return {
                "error": f"Analysis generation failed: {str(e)}"
            }

def main():
    st.title("🏀 Advanced Basketball AI Performance Analyst")
    
    # Initialize analyst with error handling
    analyst = AdvancedBasketballAnalyst()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Analysis Configuration")
        analysis_mode = st.selectbox(
            "Select Analysis Mode", 
            [
                "Comprehensive Player Analysis", 
                "Advanced Function Calling",
                "Real-time Performance Prediction"
            ]
        )
    
    # Main analysis interface
    if analysis_mode == "Comprehensive Player Analysis":
        player_name = st.text_input("Enter Player Name")
        if st.button("Analyze Player"):
            with st.spinner(f"Analyzing {player_name}..."):
                analysis = analyst.generate_comprehensive_analysis(player_name)
                st.json(analysis)
    
    elif analysis_mode == "Advanced Function Calling":
        query = st.text_area("Enter your basketball performance query")
        if st.button("Execute Advanced Analysis"):
            with st.spinner("Performing advanced analysis..."):
                result = analyst.advanced_function_calling_analysis(query)
                st.json(result)
    
    elif analysis_mode == "Real-time Performance Prediction":
        st.write("Coming soon: Real-time performance prediction")

if __name__ == "__main__":
    main()
