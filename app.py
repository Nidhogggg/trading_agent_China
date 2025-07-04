import streamlit as st
import os
import datetime
import json
from pathlib import Path
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
import pandas as pd
import chromadb
import shutil
import time
import sqlite3
import sys
import psutil

# Set page config
st.set_page_config(
    page_title="TradingAgents Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .report-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
    }
    .config-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def load_reports():
    """Load all reports from the reports directory"""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        return []
    
    reports = []
    for file in reports_dir.glob("*"):
        if file.suffix in ['.html', '.md']:
            # Parse filename to get ticker and date
            # Expected format: report_TICKER_DATE.{html|md}
            parts = file.stem.split('_')
            if len(parts) == 3:
                reports.append({
                    'ticker': parts[1],
                    'date': parts[2],
                    'path': str(file),
                    'type': file.suffix[1:]  # Remove the dot
                })
    
    return sorted(reports, key=lambda x: (x['ticker'], x['date']), reverse=True)

def force_close_chroma():
    """Force close all ChromaDB connections"""
    current_process = psutil.Process()
    
    # Get all open files for the current process and its children
    for proc in current_process.children(recursive=True):
        try:
            for file in proc.open_files():
                if 'chroma.sqlite3' in file.path:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)
                    except:
                        pass
        except:
            pass

def cleanup_memory():
    """Clean up ChromaDB collections before running new analysis"""
    # First, force close any existing ChromaDB connections
    force_close_chroma()
    
    # Wait a moment for processes to close
    time.sleep(1)
    
    # Clean up chroma_db directory
    try:
        chroma_path = Path("./chroma_db")
        if chroma_path.exists():
            # On Windows, use system commands to force delete
            if sys.platform == 'win32':
                os.system(f'rmdir /S /Q "{chroma_path}"')
            else:
                shutil.rmtree(chroma_path)
    except Exception as e:
        st.warning(f"Warning: Could not remove chroma_db directory: {str(e)}")
    
    # Wait for filesystem to sync
    time.sleep(1)
    
    # Create fresh directory
    os.makedirs("./chroma_db", exist_ok=True)

@st.cache_resource
def get_trading_graph(analysts, config):
    """Create and cache TradingGraph instance"""
    return TradingAgentsGraph(analysts, config=config, debug=True)

def run_analysis(ticker, analysis_date, selected_analysts, research_depth, 
                shallow_thinker, deep_thinker):
    """Run the trading agents analysis"""
    try:
        # Create containers for different components
        progress_container = st.empty()
        status_container = st.empty()
        message_container = st.empty()
        report_container = st.empty()
        
        # Create a container for agent status
        agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            "Portfolio Manager": "pending"
        }
        
        def update_agent_status():
            # Create status table
            status_df = pd.DataFrame([
                {"Team": "Analyst Team", "Agent": "Market Analyst", "Status": agent_status["Market Analyst"]},
                {"Team": "Analyst Team", "Agent": "Social Analyst", "Status": agent_status["Social Analyst"]},
                {"Team": "Analyst Team", "Agent": "News Analyst", "Status": agent_status["News Analyst"]},
                {"Team": "Analyst Team", "Agent": "Fundamentals Analyst", "Status": agent_status["Fundamentals Analyst"]},
                {"Team": "Research Team", "Agent": "Bull Researcher", "Status": agent_status["Bull Researcher"]},
                {"Team": "Research Team", "Agent": "Bear Researcher", "Status": agent_status["Bear Researcher"]},
                {"Team": "Research Team", "Agent": "Research Manager", "Status": agent_status["Research Manager"]},
                {"Team": "Trading Team", "Agent": "Trader", "Status": agent_status["Trader"]},
                {"Team": "Risk Team", "Agent": "Risky Analyst", "Status": agent_status["Risky Analyst"]},
                {"Team": "Risk Team", "Agent": "Neutral Analyst", "Status": agent_status["Neutral Analyst"]},
                {"Team": "Risk Team", "Agent": "Safe Analyst", "Status": agent_status["Safe Analyst"]},
                {"Team": "Risk Team", "Agent": "Portfolio Manager", "Status": agent_status["Portfolio Manager"]}
            ])
            
            # Apply color coding
            def color_status(val):
                if val == "completed":
                    return 'background-color: #90EE90'  # Light green
                elif val == "in_progress":
                    return 'background-color: #FFB6C1'  # Light pink
                return 'background-color: #F0F0F0'  # Light gray for pending
            
            # Display styled table
            with status_container:
                st.dataframe(
                    status_df.style.apply(lambda x: [color_status(val) for val in x], subset=['Status']),
                    hide_index=True,
                    use_container_width=True
                )

        # Show initial status
        with progress_container:
            st.progress(0)
        update_agent_status()
        with message_container:
            st.info("Cleaning up previous analysis data...")

        # Clean up memory before running new analysis
        cleanup_memory()

        # Create config with selected research depth
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = research_depth
        config["max_risk_discuss_rounds"] = research_depth
        config["quick_think_llm"] = shallow_thinker
        config["deep_think_llm"] = deep_thinker
        # config["project_dir"] = os.path.join(os.path.dirname(__file__), ".")

        # Update status for initialization
        with progress_container:
            st.progress(5)
        with message_container:
            st.info("Initializing analysis...")

        # Initialize the graph using cached function
        graph = get_trading_graph(
            [analyst.value for analyst in selected_analysts], 
            config
        )

        # Initialize state and get graph args
        init_agent_state = graph.propagator.create_initial_state(ticker, analysis_date)
        args = graph.propagator.get_graph_args()

        # Run the analysis
        try:
            # Update progress for analysis start
            with progress_container:
                st.progress(10)
            with message_container:
                st.info("Running market analysis...")

            # Set first analyst to in_progress
            first_analyst = f"{selected_analysts[0].value.capitalize()} Analyst"
            agent_status[first_analyst] = "in_progress"
            update_agent_status()

            final_state = graph.graph.invoke(init_agent_state, **args)

            # Process the final state to update agent statuses and reports
            if "market_report" in final_state:
                agent_status["Market Analyst"] = "completed"
                with report_container:
                    st.markdown("### Market Analysis")
                    st.markdown(final_state["market_report"])
                update_agent_status()

            if "sentiment_report" in final_state:
                agent_status["Social Analyst"] = "completed"
                with report_container:
                    st.markdown("### Social Sentiment Analysis")
                    st.markdown(final_state["sentiment_report"])
                update_agent_status()

            if "news_report" in final_state:
                agent_status["News Analyst"] = "completed"
                with report_container:
                    st.markdown("### News Analysis")
                    st.markdown(final_state["news_report"])
                update_agent_status()

            if "fundamentals_report" in final_state:
                agent_status["Fundamentals Analyst"] = "completed"
                with report_container:
                    st.markdown("### Fundamentals Analysis")
                    st.markdown(final_state["fundamentals_report"])
                update_agent_status()

            # Research Team Status
            if "investment_debate_state" in final_state:
                debate_state = final_state["investment_debate_state"]
                agent_status["Bull Researcher"] = "completed"
                agent_status["Bear Researcher"] = "completed"
                agent_status["Research Manager"] = "completed"
                with report_container:
                    st.markdown("### Research Team Analysis")
                    if "bull_history" in debate_state:
                        st.markdown("#### Bull Researcher")
                        st.markdown(debate_state["bull_history"])
                    if "bear_history" in debate_state:
                        st.markdown("#### Bear Researcher")
                        st.markdown(debate_state["bear_history"])
                    if "judge_decision" in debate_state:
                        st.markdown("#### Research Manager Decision")
                        st.markdown(debate_state["judge_decision"])
                update_agent_status()

            # Trading Team Status
            if "trader_investment_plan" in final_state:
                agent_status["Trader"] = "completed"
                with report_container:
                    st.markdown("### Trading Plan")
                    st.markdown(final_state["trader_investment_plan"])
                update_agent_status()

            # Risk Management Team Status
            if "risk_debate_state" in final_state:
                risk_state = final_state["risk_debate_state"]
                agent_status["Risky Analyst"] = "completed"
                agent_status["Safe Analyst"] = "completed"
                agent_status["Neutral Analyst"] = "completed"
                agent_status["Portfolio Manager"] = "completed"
                with report_container:
                    st.markdown("### Risk Management Analysis")
                    if "risky_history" in risk_state:
                        st.markdown("#### Risky Analyst")
                        st.markdown(risk_state["risky_history"])
                    if "safe_history" in risk_state:
                        st.markdown("#### Safe Analyst")
                        st.markdown(risk_state["safe_history"])
                    if "neutral_history" in risk_state:
                        st.markdown("#### Neutral Analyst")
                        st.markdown(risk_state["neutral_history"])
                    if "judge_decision" in risk_state:
                        st.markdown("#### Portfolio Manager Decision")
                        st.markdown(risk_state["judge_decision"])
                update_agent_status()

            # Update progress for report generation
            with progress_container:
                st.progress(90)
            with message_container:
                st.info("Generating final report...")

            # Store current state for reflection and report generation
            graph.curr_state = final_state
            graph.ticker = ticker
            
            # Log state
            graph._log_state(analysis_date, final_state)
            
            # Generate web report without re-running analysis
            graph._generate_web_report(analysis_date, final_state)

            decision = graph.process_signal(final_state["final_trade_decision"])
            
            # Show completion
            with progress_container:
                st.progress(100)
            with message_container:
                st.success("Analysis completed successfully!")

            # Clean up after successful run
            cleanup_memory()

            return decision, final_state
            
        except Exception as e:
            with message_container:
                st.error(f"Analysis failed: {str(e)}")
            # Clean up after failed run
            cleanup_memory()
            raise e

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None, None

def main():
    # Header
    st.title("TradingAgents Dashboard")
    st.markdown("---")

    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Configuration", "Reports"])

    if page == "Configuration":
        st.header("Analysis Configuration")
        
        with st.container():
            st.subheader("Basic Settings")
            col1, col2 = st.columns(2)
            
            with col1:
                ticker = st.text_input("Ticker Symbol", value="SPY")
                analysis_date = st.date_input(
                    "Analysis Date",
                    value=datetime.datetime.now().date(),
                    max_value=datetime.datetime.now().date()
                )

            with col2:
                research_depth = st.slider(
                    "Research Depth",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Number of debate rounds"
                )

        st.subheader("Analyst Selection")
        analysts = st.multiselect(
            "Select Analysts",
            options=[analyst.value for analyst in AnalystType],
            default=[AnalystType.MARKET.value, 
                     AnalystType.FUNDAMENTALS.value, 
                     AnalystType.NEWS.value, 
                     AnalystType.SOCIAL.value],
            help="Choose the analysts to include in the analysis"
        )

        st.subheader("Model Configuration")
        col1, col2 = st.columns(2)
        with col1:
            shallow_thinker = st.selectbox(
                "Quick Thinking Model",
                options=["deepseek-chat", "deepseek-reasoner"],
                index=0
            )
        with col2:
            deep_thinker = st.selectbox(
                "Deep Thinking Model",
                options=["deepseek-chat", "deepseek-reasoner"],
                index=0
            )

        if st.button("Run Analysis", type="primary"):
            if not analysts:
                st.warning("Please select at least one analyst.")
                return

            selected_analysts = [
                analyst for analyst in AnalystType 
                if analyst.value in analysts
            ]
            
            decision, final_state = run_analysis(
                ticker,
                analysis_date.strftime("%Y-%m-%d"),
                selected_analysts,
                research_depth,
                shallow_thinker,
                deep_thinker
            )

            if decision:
                st.success(f"Analysis completed successfully. Decision: {decision}")
                st.balloons()

    else:  # Reports page
        st.header("Analysis Reports")
        
        # Load and display reports
        reports = load_reports()
        
        if not reports:
            st.info("No reports found in the reports directory.")
            return

        # Create a DataFrame for better display
        df = pd.DataFrame(reports)
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            ticker_filter = st.multiselect(
                "Filter by Ticker",
                options=sorted(df['ticker'].unique()),
                default=[]
            )
        with col2:
            date_filter = st.date_input(
                "Filter by Date Range",
                value=(
                    datetime.datetime.strptime(df['date'].min(), '%Y-%m-%d').date(),
                    datetime.datetime.strptime(df['date'].max(), '%Y-%m-%d').date()
                )
            )

        # Apply filters
        filtered_df = df.copy()
        if ticker_filter:
            filtered_df = filtered_df[filtered_df['ticker'].isin(ticker_filter)]
        filtered_df = filtered_df[
            (filtered_df['date'] >= date_filter[0].strftime('%Y-%m-%d')) &
            (filtered_df['date'] <= date_filter[1].strftime('%Y-%m-%d'))
        ]

        # Display reports
        for _, report in filtered_df.iterrows():
            with st.expander(f"{report['ticker']} - {report['date']}"):
                if report['type'] == 'html':
                    with open(report['path'], 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=600, scrolling=True)
                else:  # Markdown
                    with open(report['path'], 'r', encoding='utf-8') as f:
                        st.markdown(f.read())
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    with open(report['path'], 'r', encoding='utf-8') as f:
                        st.download_button(
                            f"Download {report['type'].upper()}",
                            f.read(),
                            file_name=os.path.basename(report['path']),
                            mime=f"text/{report['type']}"
                        )
                
                # If HTML exists, also show MD download button
                if report['type'] == 'html':
                    md_path = report['path'].replace('.html', '.md')
                    if os.path.exists(md_path):
                        with col2:
                            with open(md_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "Download MD",
                                    f.read(),
                                    file_name=os.path.basename(md_path),
                                    mime="text/markdown"
                                )

if __name__ == "__main__":
    main() 