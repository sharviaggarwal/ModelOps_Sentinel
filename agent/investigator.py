
from click import prompt

from backend.database.connection import SessionLocal
from backend.database.models import Incident, MonitoringRun
from langgraph.graph import StateGraph, START, END
from agent.state import InvestigationState
import sqlite3
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_ollama import ChatOllama
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

checkpoint_connection = sqlite3.connect(
    "agent_checkpoints.sqlite",
    check_same_thread=False
)

checkpointer = SqliteSaver(checkpoint_connection)

def fetch_incident_node(state):

    db = SessionLocal()

    try:
        # Step 1: Fetch incident using its ID
        incident = db.query(Incident).filter(
            Incident.id == state["incident_id"]
        ).first()

        if not incident:
            return {
                "error": f"Incident {state['incident_id']} not found"
            }

        # Step 2: Fetch the monitoring run linked to this incident
        monitoring_run = db.query(MonitoringRun).filter(
            MonitoringRun.id == incident.monitoring_run_id
        ).first()

        if not monitoring_run:
            return {
                "error": "Monitoring report not found"
            }

        # Step 3: Prepare incident information
        incident_data = {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "source": incident.source,
            "status": incident.status,
            "created_at": incident.created_at.isoformat()
        }

        # Step 4: Return information to LangGraph state
        return {
            "incident": incident_data,
            "monitoring_report": monitoring_run.monitoring_report,
            "error": None
        }

    except Exception as e:
        return {
            "error": str(e)
        }

    finally:
        db.close()

import json




def analyze_incident_node(state):
    if state.get("error"):
        return {}

    incident = state["incident"]
    monitoring_report = state["monitoring_report"]

    prompt = f"""
You are an experienced Machine Learning Operations (MLOps) engineer
investigating production ML model incidents.

Your task is to investigate the incident using the evidence provided.

INCIDENT DETAILS:
{json.dumps(incident, indent=2)}

MONITORING REPORT:
{json.dumps(monitoring_report, indent=2)}

Prepare a detailed investigation using the following structure:

1. INCIDENT SUMMARY
Explain what happened and why this incident was triggered.

2. ROOT CAUSE ANALYSIS
Identify the most likely cause based on the available monitoring evidence.
Clearly distinguish confirmed findings from possible explanations.

3. SUPPORTING EVIDENCE
List the relevant metrics, statistical tests, and monitoring observations
that support your analysis.

4. RECOMMENDED ACTIONS
Suggest practical steps to investigate and resolve the issue.
Prioritize the most important actions.

5. POTENTIAL IMPACT
Explain what could happen if the issue remains unresolved.

IMPORTANT RULES:
- Use only the evidence provided.
- Never invent metrics or monitoring results.
- Data drift does not automatically prove model performance degradation.
- Clearly mention when evidence is insufficient.
- Do not claim that any recommended action has already been executed.
- Keep recommendations practical and technically relevant.

Return the investigation in readable Markdown.
"""

    try:
        print("STEP 1: Sending investigation prompt to Ollama...")

        response = llm.invoke(prompt)

        print("STEP 2: Ollama response received!")


        investigation = response.content

        return {
            "investigation": investigation,
            "error": None
        }

    except Exception as e:
        return {
            "error": f"Investigation failed: {str(e)}"
        }


from langgraph.types import interrupt


def human_approval_node(state):

    # Pause the workflow and ask for human approval
    approval = interrupt({
        "message": "AI investigation completed. Review the recommendations before proceeding.",
        "incident": state["incident"],
        "investigation": state["investigation"],
        "question": "Do you approve these recommendations?"
    })

    # Save the human's decision
    return {
        "approval_status": approval
    }

def route_after_fetch(state):

    if state.get("error"):
        return "end"

    return "analyze"
def build_investigator():

    workflow = StateGraph(InvestigationState)

    workflow.add_node("fetch_incident", fetch_incident_node)
    workflow.add_node("analyze_incident", analyze_incident_node)
    workflow.add_node("human_approval", human_approval_node)

    workflow.add_edge(START, "fetch_incident")

    workflow.add_conditional_edges(
        "fetch_incident",
        route_after_fetch,
        {
            "analyze": "analyze_incident",
            "end": END
        }
    )

    workflow.add_edge("analyze_incident", "human_approval")
    workflow.add_edge("human_approval", END)

    return workflow.compile(checkpointer=checkpointer)
checkpointer = SqliteSaver(checkpoint_connection)
checkpointer.setup()

def resume_investigation(thread_id, decision):

    if decision not in ["APPROVED", "REJECTED"]:
        raise ValueError(
            "Decision must be APPROVED or REJECTED"
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = app.invoke(
        Command(resume=decision),
        config=config
    )

    return result
app=build_investigator()