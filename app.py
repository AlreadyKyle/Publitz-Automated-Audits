import streamlit as st
import os
from datetime import datetime
from src.ai_generator import AIGenerator
from src.game_search import GameSearch
from src.steamdb_scraper import SteamDBScraper

# Page config
st.set_page_config(page_title="Publitz Automated Audits", page_icon="📊", layout="wide")

# Initialize session state
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

def main():
    st.title("📊 Publitz Automated Game Audits")
    st.markdown("---")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))

        if not api_key:
            st.error("⚠️ Please enter your Anthropic API Key")
            st.stop()

        st.markdown("---")
        st.markdown("### Report Type")
        report_type = st.radio("Select Report Type", ["Pre-Launch", "Post-Launch"])

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        game_name = st.text_input("🎮 Enter Game Name", placeholder="e.g., Defense Of Fort Burton")

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🚀 Generate Audit Report", type="primary", use_container_width=True)

    if generate_button and game_name:
        try:
            # Initialize components
            game_search = GameSearch()
            steamdb_scraper = SteamDBScraper()
            ai_generator = AIGenerator(api_key)

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Search for game
            status_text.text("🔍 Searching for game...")
            progress_bar.progress(10)

            game_data = game_search.search_game(game_name)

            if not game_data:
                st.error(f"❌ Game '{game_name}' not found. Please check the name and try again.")
                st.stop()

            st.success(f"✅ Found game: {game_data['name']}")
            progress_bar.progress(25)

            # Step 2: Find competitor games
            status_text.text("🔍 Finding competitor games...")
            competitor_data = game_search.find_competitors(game_data, min_competitors=3, max_competitors=10)

            num_competitors = len(competitor_data)
            if num_competitors == 0:
                st.warning("⚠️ No competitors found initially, expanding search criteria...")
                # Use broader search criteria
                competitor_data = game_search.find_competitors_broad(game_data, min_competitors=5)
                num_competitors = len(competitor_data)

            st.success(f"✅ Found {num_competitors} competitor games")
            progress_bar.progress(50)

            # Step 3: Gather Steam data
            status_text.text("📊 Gathering Steam data...")
            sales_data = steamdb_scraper.get_sales_data(game_data['app_id'])
            progress_bar.progress(65)

            # Step 4: Gather competitor Steam data
            status_text.text("📊 Gathering competitor data...")
            for i, competitor in enumerate(competitor_data):
                competitor['steam_data'] = steamdb_scraper.get_sales_data(competitor['app_id'])
            progress_bar.progress(75)

            # Step 5: Generate report using AI
            status_text.text("🤖 Generating AI-powered audit report...")

            if report_type == "Post-Launch":
                report_data = ai_generator.generate_post_launch_report(
                    game_data,
                    sales_data,
                    competitor_data,
                    steamdb_data=sales_data
                )
            else:
                report_data = ai_generator.generate_pre_launch_report(
                    game_data,
                    competitor_data
                )

            progress_bar.progress(100)
            status_text.text("✅ Report generated successfully!")

            # Display results
            st.markdown("---")
            st.markdown("## 📋 Audit Report")

            # Display summary boxes
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Report Type", report_type)
            with col2:
                st.metric("Competitors Found", num_competitors)
            with col3:
                if sales_data:
                    st.metric("Estimated Revenue", sales_data.get('estimated_revenue', 'N/A'))

            # Display full report
            st.markdown("### 📝 Full Report")
            st.markdown(report_data)

            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{game_name.replace(' ', '_')}_{report_type}_Report_{timestamp}.md"

            st.download_button(
                label="📥 Download Report",
                data=report_data,
                file_name=filename,
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()
