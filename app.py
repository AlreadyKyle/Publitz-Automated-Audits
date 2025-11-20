"""Streamlit app for Publitz Automated Steam Audit Tool."""

import streamlit as st
import sys
import os
from datetime import datetime
from io import BytesIO

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.steam_scraper import SteamScraper
from src.steamdb_scraper import SteamDBScraper
from src.ai_generator import AIReportGenerator
from src.report_generator import ReportGenerator
from src.utils import extract_app_id, is_valid_steam_url, detect_launch_status


# Page config
st.set_page_config(
    page_title="Publitz Steam Audit Tool",
    page_icon="🎮",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #0066cc;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 2rem;
}
.status-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.status-info {
    background-color: #d1ecf1;
    border-left: 4px solid #17a2b8;
}
.status-success {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
}
.status-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}
.status-error {
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">🎮 Publitz Steam Audit Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Steam launch readiness and performance reports</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv('ANTHROPIC_API_KEY', ''),
            help="Your Claude API key (or set ANTHROPIC_API_KEY in .env)"
        )

        st.divider()

        st.header("ℹ️ About")
        st.markdown("""
This tool automatically:
- Scrapes Steam store data
- Collects competitive intel
- Detects pre/post launch
- Generates AI-powered audit reports
- Exports professional PDFs

**Report Types:**
- **Pre-Launch:** Store optimization, pricing strategy, launch timing
- **Post-Launch:** Performance analysis, revenue recovery, live-ops roadmap
        """)

        st.divider()

        st.markdown("Made by Kyle Smith")

    # Main content
    steam_url = st.text_input(
        "Steam Store Page URL",
        placeholder="https://store.steampowered.com/app/1234567/GameName/",
        help="Paste the full Steam store page URL"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        generate_button = st.button("🚀 Generate Report", type="primary", use_container_width=True)

    with col2:
        if st.session_state.get('report_generated'):
            if st.button("🔄 Generate New Report", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    # Process
    if generate_button:
        if not steam_url:
            st.error("❌ Please enter a Steam store page URL")
            return

        if not is_valid_steam_url(steam_url):
            st.error("❌ Invalid Steam URL. Please provide a valid Steam store page URL.")
            return

        if not api_key:
            st.error("❌ Please provide your Anthropic API key in the sidebar")
            return

        # Extract app ID
        app_id = extract_app_id(steam_url)

        # Process
        try:
            with st.spinner("🔍 Analyzing game..."):
                # Initialize scrapers
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Scrape Steam
                status_text.markdown('<div class="status-box status-info">📥 Scraping Steam store page...</div>', unsafe_allow_html=True)
                progress_bar.progress(15)

                steam_scraper = SteamScraper()
                game_data = steam_scraper.scrape_game(app_id)

                st.success(f"✅ Found game: **{game_data.get('name')}**")

                # Step 2: Detect launch status
                status_text.markdown('<div class="status-box status-info">🔍 Detecting launch status...</div>', unsafe_allow_html=True)
                progress_bar.progress(25)

                launch_status = detect_launch_status(
                    game_data.get('release_date'),
                    game_data.get('coming_soon', False)
                )

                report_type = "Pre-Launch" if launch_status == "pre_launch" else "Post-Launch"
                st.info(f"🎯 Report Type: **{report_type}**")

                # Step 3: Scrape SteamDB
                status_text.markdown('<div class="status-box status-info">📊 Gathering competitive data from SteamDB...</div>', unsafe_allow_html=True)
                progress_bar.progress(40)

                steamdb_scraper = SteamDBScraper()
                steamdb_data = steamdb_scraper.scrape_game_data(app_id)

                # Step 4: Find competitors
                status_text.markdown('<div class="status-box status-info">🔎 Finding competitor games...</div>', unsafe_allow_html=True)
                progress_bar.progress(50)

                tags = game_data.get('tags', [])
                competitor_data = steamdb_scraper.search_similar_games(tags, limit=3)

                # Enrich competitor data
                for comp in competitor_data:
                    try:
                        comp_game_data = steam_scraper.scrape_game(comp['app_id'])
                        comp.update({
                            'screenshots': comp_game_data.get('screenshots', []),
                            'description': comp_game_data.get('short_description', ''),
                            'review_score': comp_game_data.get('reviews', {}).get('summary', 'N/A'),
                        })
                    except:
                        pass

                st.success(f"✅ Found {len(competitor_data)} competitor games")

                # Step 5: Generate AI report
                status_text.markdown('<div class="status-box status-info">🤖 Generating AI-powered audit report...</div>', unsafe_allow_html=True)
                progress_bar.progress(70)

                ai_generator = AIReportGenerator(api_key=api_key)

                if launch_status == "pre_launch":
                    report_data = ai_generator.generate_pre_launch_report(
                        game_data, competitor_data, steamdb_data
                    )
                else:
                    # For post-launch, we'd need sales data from Steam Partner
                    # For now, use available data
                    sales_data = {
                        'reviews': game_data.get('reviews', {}),
                        'followers': steamdb_data.get('followers'),
                    }
                    report_data = ai_generator.generate_post_launch_report(
                        game_data, sales_data, competitor_data, steamdb_data
                    )

                report_data['generated_at'] = datetime.now().isoformat()

                st.success("✅ Report generated successfully!")

                # Step 6: Generate PDF
                status_text.markdown('<div class="status-box status-info">📄 Creating PDF report...</div>', unsafe_allow_html=True)
                progress_bar.progress(90)

                report_generator = ReportGenerator()
                pdf_buffer = report_generator.generate_pdf(report_data)

                progress_bar.progress(100)
                status_text.markdown('<div class="status-box status-success">✅ Report complete!</div>', unsafe_allow_html=True)

                # Store in session state
                st.session_state['report_data'] = report_data
                st.session_state['pdf_buffer'] = pdf_buffer
                st.session_state['report_generated'] = True

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
            return

    # Display report if generated
    if st.session_state.get('report_generated'):
        st.divider()
        st.header("📊 Generated Report")

        report_data = st.session_state['report_data']
        pdf_buffer = st.session_state['pdf_buffer']

        # Download button
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            game_name = report_data.get('game_name', 'game').replace(' ', '_')
            report_type = report_data.get('report_type', 'audit')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{game_name}_{report_type}_{timestamp}.pdf"

            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )

        with col2:
            # Generate markdown for preview
            report_generator = ReportGenerator()
            markdown_preview = report_generator.generate_markdown_preview(report_data)

            st.download_button(
                label="📥 Download Markdown",
                data=markdown_preview,
                file_name=filename.replace('.pdf', '.md'),
                mime="text/markdown",
                use_container_width=True
            )

        # Preview tabs
        tab1, tab2 = st.tabs(["📄 Report Preview", "ℹ️ Metadata"])

        with tab1:
            st.markdown(report_data.get('report_text', 'No content'))

        with tab2:
            st.json({
                'game_name': report_data.get('game_name'),
                'report_type': report_data.get('report_type'),
                'generated_at': report_data.get('generated_at'),
            })


if __name__ == "__main__":
    main()
