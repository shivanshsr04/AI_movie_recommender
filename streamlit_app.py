"""Guest-accessible movie discovery with real content inference."""
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from app_service import artifact_signature, load_catalog, recommend
from data_loader import ROOT

st.set_page_config(page_title='Movie Recommendation Explorer', page_icon='🎬', layout='wide')


@st.cache_resource
def cached_catalog(model_dir, signature):
    return load_catalog(model_dir)


def main():
    st.title('Movie Recommendation Explorer')
    st.caption('Find related movies and compare content similarity with popularity.')
    model_dir = Path(os.environ.get('MOVIE_MODEL_DIR', str(ROOT / 'models')))
    try:
        movies, model, metadata = cached_catalog(str(model_dir), artifact_signature(model_dir))
    except (ValueError, OSError, KeyError) as exc:
        st.error(f'Could not load the movie catalog: {exc}')
        st.stop()
    if metadata['demo']:
        st.info('Demo mode: 12 fictional movies with authored descriptions. These examples show how similarity works; they are not real movie ratings or benchmark results.')
    else:
        st.caption(f"Dataset: {metadata['source']} · {len(movies):,} movies")
    page = st.sidebar.radio('Explore', ['Recommendations', 'Search', 'Analytics', 'About'])
    if page == 'Recommendations':
        methods = ['Content similarity']
        if not metadata['demo']:
            methods.append('Popularity baseline')
        method = st.selectbox('Recommendation method', methods)
        ids = movies.movieId.tolist()
        titles = movies.set_index('movieId').title.to_dict()
        seed_id = st.selectbox('Choose a movie', ids, format_func=lambda mid: f'{titles[mid]} · #{mid}')
        k = st.slider('Number of recommendations', 1, min(20, max(1, len(movies) - 1)), min(5, max(1, len(movies) - 1)))
        if st.button('Find movies', type='primary'):
            results = recommend(movies, model, seed_id, method, k)
            st.subheader(f'Movies to explore after {titles[seed_id]}')
            if not results:
                st.warning('No recommendations available for this selection.')
            for rank, (movie_id, score) in enumerate(results, 1):
                movie = movies.loc[movies.movieId == movie_id].iloc[0]
                with st.container(border=True):
                    st.markdown(f'**{rank}. {movie.title}**')
                    st.caption(movie.genres.replace('|', ' · ') or 'Genres unavailable')
                    if method == 'Content similarity':
                        st.write(f'Cosine similarity: {score:.3f}')
                    else:
                        st.write(f'Rating count: {int(score):,}')
                    if movie.overview:
                        st.write(movie.overview)
            st.caption('Similarity measures shared text and genres; it is not a probability that you will like a movie.' if method == 'Content similarity' else 'Popularity counts ratings across the catalog. It does not use personal preferences.')
    elif page == 'Search':
        term = st.text_input('Search titles', placeholder='Enter part of a title')
        matches = movies[movies.title.str.contains(term, case=False, na=False, regex=False)] if term else movies
        st.caption(f'{len(matches):,} matching movies · showing up to 100')
        st.dataframe(matches[['movieId', 'title', 'genres']].head(100), hide_index=True, use_container_width=True)
    elif page == 'Analytics':
        col1, col2 = st.columns(2)
        col1.metric('Movies', f'{len(movies):,}')
        col2.metric('Ratings', f"{int(movies.rating_count.sum()):,}")
        st.subheader('Movies by genre')
        genres = movies.genres.str.split('|').explode()
        st.bar_chart(genres[genres.ne('')].value_counts())
        if not metadata['demo']:
            st.subheader('Most rated movies')
            st.dataframe(movies.nlargest(20, 'rating_count')[['title', 'rating_count', 'mean_rating']], hide_index=True)
            st.subheader('Movie release years')
            years = pd.to_numeric(movies.title.str.extract(r'\((\d{4})\)\s*$')[0], errors='coerce').dropna().astype(int)
            st.line_chart(years.value_counts().sort_index())
    else:
        st.markdown('''### How it works
Titles and optional descriptions become TF-IDF features. Genre indicators form a separate feature block. Cosine similarity ranks movies using the combined sparse features.

**Available here:** content similarity and, with MovieLens data, a rating-count popularity baseline.

**Offline experiments:** user-based collaborative filtering, TruncatedSVD and reciprocal-rank hybrid fusion. These require historical user ratings and are not connected to guest identities.

**Limitations:** MovieLens small has titles and genres but no plot summaries. Similarity is not a calibrated confidence score. There is no production user-profile or feedback system.

Built by Shivansh Srivastava. See the repository README for reproducible evaluation and data attribution.''')


if __name__ == '__main__':
    main()
