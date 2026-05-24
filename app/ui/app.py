"""Streamlit application for the restaurant recommendation system."""

from __future__ import annotations

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from app.data import store
from app.models import UserPreferences
from app.services import recommend


@st.cache_data(show_spinner=False)
def load_ui_data() -> tuple[list[str], list[str]]:
    store.load_catalog()
    locations = store.get_distinct_locations()
    cuisines = store.get_distinct_cuisines()
    return locations, cuisines


def _inject_css() -> None:
    try:
        with open("app/ui/styles.css", "r", encoding="utf-8") as fh:
            css = fh.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # OK if CSS not present
        pass


def format_cost(cost: str) -> str:
    return cost


def build_user_preferences(locations: list[str], cuisines: list[str]) -> UserPreferences:
    with st.form("preferences_form"):
        st.markdown("<div class=hero>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            # If the catalog contains only one city, surface neighborhoods as the primary location choice.
            if len(locations) == 1:
                selected_city = locations[0]
                st.markdown(f"**City:** {selected_city}")
                area_options = store.get_distinct_areas(selected_city)
                if area_options:
                    location_choice = st.selectbox(
                        f"Select a neighborhood in {selected_city}",
                        options=["Any"] + area_options,
                        key="location_area"
                    )
                    st.caption(
                        "The catalog is currently for Bangalore, so the location lookup uses Bangalore neighborhoods."
                    )
                else:
                    location_choice = "Any"
                location = selected_city
            else:
                location = st.selectbox("City", options=locations)
                area_options = store.get_distinct_areas(location)
                if area_options:
                    location_choice = st.selectbox("Area (optional)", options=["Any"] + area_options)
                else:
                    location_choice = "Any"
            cuisine_choice = st.selectbox("Cuisine", options=["Any"] + cuisines)
        with col2:
            budget = st.selectbox("Budget", options=["low", "medium", "high"], index=1)

        if area_options:
            st.caption("Filter within the selected city by neighborhood/area.")

        min_rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.5)
        additional_preferences = st.text_area(
            "Additional preferences (optional)",
            placeholder="E.g. outdoor seating, quick delivery, family-friendly",
            max_chars=200,
        )
        submitted = st.form_submit_button("Find Matches")

        if not submitted:
            st.info("Choose your preferences and click Find Matches to see best matches.")
            st.stop()

        return UserPreferences(
            location=location,
            area="" if location_choice == "Any" else location_choice,
            budget=budget,
            cuisine="" if cuisine_choice == "Any" else cuisine_choice,
            minRating=min_rating,
            additionalPreferences=additional_preferences,
        )


def _render_pick_of_the_day() -> None:
    st.markdown("## AI Pick of the Day")
    left, right = st.columns([2, 3])
    with left:
        st.image("https://images.unsplash.com/photo-1544025162-d76694265947?w=1200", use_column_width=True)
    with right:
        st.markdown("### Sushi Nakazawa")
        st.write("Based on your recent preferences, this is a great match.")
        st.markdown("[Book a Table](#)")


def render_recommendations(response) -> None:
    if response.summary:
        st.markdown(f"### Summary\\n{response.summary}")

    if response.meta is not None and response.meta.used_fallback:
        st.warning(
            "The recommendation engine used a fallback ranking path due to LLM unavailability or response parsing issues."
        )

    if not response.recommendations:
        st.info("No restaurants matched your filtered preferences.")
        if response.suggestions:
            st.markdown("#### Suggestions to broaden your search")
            for suggestion in response.suggestions:
                st.write(f"- {suggestion}")
        return

    for rec in response.recommendations:
        with st.container():
            cols = st.columns([2, 3])
            with cols[0]:
                st.image("https://images.unsplash.com/photo-1544025162-d76694265947?w=800", use_column_width=True)
            with cols[1]:
                st.markdown(f"### {rec.name}  ")
                if getattr(rec, 'area', None):
                    st.markdown(f"**Area:** {rec.area}")
                st.markdown(f"**Cuisine:** {', '.join(rec.cuisine)}")
                st.markdown(f"**Rating:** {rec.rating} — **Cost:** {format_cost(rec.estimated_cost)}")
                st.write(rec.explanation)

    if response.meta is not None:
        st.caption(
            f"Candidates considered: {response.meta.candidates_considered} · "
            f"Filters applied: {', '.join(response.meta.filters_applied)}"
        )


def main() -> None:
    st.set_page_config(page_title="GastroAI — Recommendations", layout="wide")
    _inject_css()

    st.markdown("<div class=brand>GastroAI</div>", unsafe_allow_html=True)
    st.markdown("<h1 class=hero-title>Discover your next obsession.</h1>", unsafe_allow_html=True)

    try:
        locations, cuisines = load_ui_data()
    except Exception as exc:
        st.error(f"Failed to load restaurant catalog: {exc}")
        return

    if not locations:
        st.warning("No locations were loaded from the restaurant catalog.")
        return

    # Render hero pick and brief UI
    _render_pick_of_the_day()

    preferences = build_user_preferences(locations, cuisines)

    try:
        with st.spinner("Ranking restaurants with the LLM..."):
            response = recommend(preferences)
    except ValueError as exc:
        st.error(f"Invalid preferences: {exc}")
        return
    except Exception as exc:
        st.error(f"Recommendation failed: {exc}")
        return

    render_recommendations(response)


if __name__ == "__main__":
    main()

