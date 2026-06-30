import json

import streamlit as st
import plotly.express as px

from analytics import (
    load_postings,
    get_summary_stats,
    get_top_skills,
    get_seniority_breakdown,
    get_search_term_breakdown,
    get_relevance_breakdown,
    get_skill_source_breakdown,
    load_skill_snapshots,
    get_top_companies,
    get_top_locations,
    get_salary_by_search_term,
)


def format_skills(skills_text):
    if not skills_text:
        return ""

    try:
        skills = json.loads(skills_text)
    except Exception:
        return ""

    skill_names = []

    for item in skills:
        if isinstance(item, dict):
            skill = item.get("skill")
        else:
            skill = item

        if skill:
            skill_names.append(str(skill))

    return ", ".join(skill_names)


st.set_page_config(
    page_title="st Radar",
    layout="wide"
)


st.title("AI Skills Radar")
st.subheader("Live Australian AI & Data Job Market Intelligence")

st.write(
    "This dashboard analyzes Australian AI and data job postings, "
    "extracts skills using a hybrid dictionary + LLM pipeline, "
    "filters noisy roles, and tracks skill demand over time."
)

df = load_postings()

st.sidebar.header("Filters")

search_terms = sorted(df["search_term"].dropna().unique())
selected_search_terms = st.sidebar.multiselect(
    "Search term",
    search_terms,
    default=search_terms
)

seniorities = sorted(df["seniority"].fillna("unclear").unique())
selected_seniorities = st.sidebar.multiselect(
    "Seniority",
    seniorities,
    default=seniorities
)

relevant_only = st.sidebar.checkbox(
    "Relevant jobs only",
    value=False
)

filtered_df = df[df["search_term"].isin(selected_search_terms)]

filtered_df = filtered_df[
    filtered_df["seniority"]
    .fillna("unclear")
    .isin(selected_seniorities)
]

if relevant_only:
    filtered_df = filtered_df[filtered_df["is_relevant"] == 1]

stats = get_summary_stats(filtered_df)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Jobs", stats["total_jobs"])
col2.metric("Relevant Jobs", stats["relevant_jobs"])
col3.metric("Irrelevant Jobs", stats["irrelevant_jobs"])
col4.metric("Extraction Failures", stats["extraction_failures"])
col5.metric("Unique Skills", stats["unique_skills"])

st.divider()

top_skills = get_top_skills(filtered_df, limit=15)

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Top 15 Most In-Demand Skills")

    if top_skills.empty:
        st.info("No skills found for the selected filters.")
    else:
        fig = px.bar(
            top_skills,
            x="frequency",
            y="skill",
            orientation="h",
            text="frequency",
            title="Top Skills",
            hover_data=["% of Relevant Jobs"]
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=560,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Seniority Breakdown")

    seniority_df = get_seniority_breakdown(filtered_df)

    if seniority_df.empty:
        st.info("No seniority data found.")
    else:
        fig = px.pie(
            seniority_df,
            names="seniority",
            values="count",
            title="Seniority Breakdown"
        )
        fig.update_layout(height=560)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Jobs by Search Term")

    search_df = get_search_term_breakdown(filtered_df)

    if search_df.empty:
        st.info("No search term data found.")
    else:
        fig = px.bar(
            search_df,
            x="search_term",
            y="count",
            text="count",
            title="Jobs by Search Term"
        )
        fig.update_layout(
            xaxis_tickangle=-20,
            height=500,
            margin=dict(l=20, r=20, t=50, b=100)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.subheader("Relevant vs Irrelevant Jobs")

    relevance_df = get_relevance_breakdown(filtered_df)

    if relevance_df.empty:
        st.info("No relevance data found.")
    else:
        fig = px.pie(
            relevance_df,
            names="relevance",
            values="count",
            title="Relevant vs Irrelevant"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

col_g, col_h = st.columns(2)

with col_g:
    st.subheader("Top Hiring Companies")

    companies_df = get_top_companies(filtered_df)

    if companies_df.empty:
        st.info("No company data found.")
    else:
        fig = px.bar(
            companies_df,
            x="count",
            y="company",
            orientation="h",
            text="count",
            title="Top Companies Hiring for AI/Data Roles"
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_h:
    st.subheader("Top Hiring Locations")

    locations_df = get_top_locations(filtered_df)

    if locations_df.empty:
        st.info("No location data found.")
    else:
        fig = px.bar(
            locations_df,
            x="count",
            y="location",
            orientation="h",
            text="count",
            title="Top Locations for AI/Data Roles"
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Salary Insights")

salary_df = get_salary_by_search_term(filtered_df)

if salary_df.empty:
    st.info("Salary data is not available for the current filtered jobs.")
else:
    fig = px.bar(
        salary_df,
        x="search_term",
        y="avg_salary",
        text="avg_salary",
        title="Average Salary by Search Term"
    )
    fig.update_layout(
        xaxis_tickangle=-20,
        height=500,
        margin=dict(l=20, r=20, t=50, b=100)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_e, col_f = st.columns(2)

with col_e:
    st.subheader("Skill Extraction Source Mix")

    source_df = get_skill_source_breakdown(filtered_df)

    if source_df.empty:
        st.info("No sourced skill data found.")
    else:
        fig = px.bar(
            source_df,
            x="source",
            y="count",
            color="source",
            text="count",
            title="Dictionary vs LLM-Inferred Skills"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

with col_f:
    st.subheader("Skill Trends Over Time")

    try:
        snapshots_df = load_skill_snapshots()

        if snapshots_df.empty:
            st.info("No historical snapshots found yet. Run save_snapshot.py to create one.")

        elif snapshots_df["snapshot_date"].nunique() < 2:
            st.info(
                "Historical trends will appear after multiple daily snapshots are collected."
            )

        else:
            top_snapshot_skills = (
                snapshots_df
                .groupby("skill")["frequency"]
                .max()
                .sort_values(ascending=False)
                .head(5)
                .index
                .tolist()
            )

            trend_df = snapshots_df[
                snapshots_df["skill"].isin(top_snapshot_skills)
            ]

            fig = px.line(
                trend_df,
                x="snapshot_date",
                y="frequency",
                color="skill",
                markers=True,
                title="Top Skills Trend Over Time"
            )

            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

    except Exception:
        st.info("Historical trend chart will appear after snapshots are available.")

st.divider()

st.markdown("## Top 20 Skills Table")

top_20 = get_top_skills(filtered_df, limit=20)

if top_20.empty:
    st.info("No skill data available.")
else:
    st.dataframe(
        top_20,
        use_container_width=True,
        hide_index=True
    )

st.markdown("## Job Postings")

show_irrelevant_in_table = st.checkbox(
    "Show irrelevant jobs in table",
    value=False
)

table_df = filtered_df.copy()

if not show_irrelevant_in_table:
    table_df = table_df[table_df["is_relevant"] == 1]

table_df["skills"] = table_df["extracted_skills"].apply(format_skills)
table_df["job_link"] = table_df["url"]

display_columns = [
    "title",
    "company",
    "location",
    "search_term",
    "seniority",
    "is_relevant",
    "skills",
    "job_link"
]

csv = table_df[display_columns].to_csv(index=False)

st.download_button(
    label="Download Filtered Jobs as CSV",
    data=csv,
    file_name="ai_skills_radar_filtered_jobs.csv",
    mime="text/csv"
)

st.dataframe(
    table_df[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "job_link": st.column_config.LinkColumn(
            "Job Link",
            display_text="View Job"
        )
    }
)