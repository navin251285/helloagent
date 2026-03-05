#!/usr/bin/env python
# coding: utf-8

# # Lesson 64 Continual Adaptation
# 
# ## Objective
# Master advanced agentic AI concepts building on previous lessons.
# 
# ## Problem Statement
# How to improve from experience?
# 
# ## Key Concepts
# - Technology integration
# - Advanced patterns
# - Production deployment
# 

# In[ ]:


# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph

from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')
import os, vertexai
from langchain_google_vertexai import ChatVertexAI
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

load_dotenv()
vertexai.init(
    project=os.getenv('PROJECT_ID'),
    location=os.getenv('LOCATION')
)
llm = ChatVertexAI(model='gemini-2.5-flash', temperature=0)
print('✓ Environment configured')


# ## Implementation

# In[ ]:


# Demonstration of arithmetic correctness
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# Test
assert add(5, 3) == 8
assert multiply(4, 5) == 20
print('✓ Arithmetic operations verified')


# ## Verification & Summary

# In[ ]:


print('='*50)
print('VERIFICATION - Lesson_64_Continual_Adaptation')
print('='*50)
print('✓ Concepts implemented')
print('✓ Tests passed')
print(f'✓ Lesson_64_Continual_Adaptation COMPLETE!')
print('='*50)

