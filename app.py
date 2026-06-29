import streamlit as st
import plotly.express as px

from analytics import (
    load_postings,
    get_summary_stats,
    get_top_skills,
    get_seniority_breakdown,
    get_search_term_breakdown,
    get_relevance_breakdown,
    get_skill_source_breakdown
)

st.set_page_config(
    page_title="AI Skills Radar",
    page_icon="📡",
    layout="wide"
)

st.title("📡 AI Skills Radar")
st.write(
    "A dashboard that analyzes live Australian AI and data job postings "
    "to identify in-demand skills, seniority levels, and noisy search results."
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

filtered_df = df[
    df["search_term"].isin(selected_search_terms)
]

filtered_df = filtered_df[
    filtered_df["seniority"].fillna("unclear").isin(selected_seniorities)
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
            title="Top Skills"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

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
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top 20 Skills Table")

top_20 = get_top_skills(filtered_df, limit=20)

if top_20.empty:
    st.info("No skill data available.")
else:
    st.dataframe(
        top_20,
        use_container_width=True,
        hide_index=True
    )

st.subheader("Job Postings")

show_irrelevant_in_table = st.checkbox(
    "Show irrelevant jobs in table",
    value=False
)

table_df = filtered_df.copy()

if not show_irrelevant_in_table:
    table_df = table_df[table_df["is_relevant"] == 1]

table_df = table_df[
    [
        "title",
        "company",
        "location",
        "search_term",
        "seniority",
        "is_relevant",
        "extracted_skills",
        "url"
    ]
]

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)
