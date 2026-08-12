import streamlit as st
import tempfile
import os

from speech_service import transcribe_audio
from language_service import extract_key_phrases, generate_summary


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Lecture Voice-to-Notes",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM COLORS AND UI
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       PAGE BACKGROUND
    ======================================================== */

    .stApp {
        background: linear-gradient(
            135deg,
            #F3F0FF 0%,
            #EEF2FF 50%,
            #F5F3FF 100%
        );
    }


    /* ========================================================
       CENTERED SECTION HEADINGS
    ======================================================== */

    .center-heading {
        text-align: center;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 20px;
    }


    /* ========================================================
       CENTERED FOOTER
    ======================================================== */

    .center-footer {
        text-align: center;
        width: 100%;
        margin-top: 10px;
        margin-bottom: 10px;
        color: #6B7280;
        font-size: 14px;
    }


    /* ========================================================
       CENTER TABS
    ======================================================== */

    button[data-baseweb="tab"] {
        justify-content: center;
        text-align: center;
        font-weight: 600;
    }


    /* ========================================================
       FILE UPLOADER
    ======================================================== */

    [data-testid="stFileUploader"] {
        background: #EDE9FE;
        border: 2px dashed #8B5CF6;
        border-radius: 14px;
        padding: 12px;
    }


    /* ========================================================
       DOWNLOAD BUTTON
    ======================================================== */

    .stDownloadButton > button {
        background: linear-gradient(
            135deg,
            #7C3AED,
            #4F46E5
        );
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
    }


    .stDownloadButton > button:hover {
        background: linear-gradient(
            135deg,
            #6D28D9,
            #4338CA
        );
        color: white;
    }


    /* ========================================================
       PRIMARY BUTTON
    ======================================================== */

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #7C3AED,
            #4F46E5
        );
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
    }


    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(
            135deg,
            #6D28D9,
            #4338CA
        );
        color: white;
    }


    /* ========================================================
       METRIC CARDS
    ======================================================== */

    [data-testid="stMetric"] {
        background: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #DDD6FE;
        box-shadow: 0 4px 14px rgba(76, 29, 149, 0.08);
    }


    /* ========================================================
       PROCESSING / STATUS AREA
    ======================================================== */

    [data-testid="stStatusWidget"] {
        background: #EDE9FE;
        border: 1px solid #C4B5FD;
        border-radius: 14px;
    }


    /* ========================================================
       AUDIO PLAYER
    ======================================================== */

    audio {
        width: 100%;
        border-radius: 10px;
    }


    /* ========================================================
       TEXT AREA
    ======================================================== */

    textarea {
        border-radius: 12px !important;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "key_phrases" not in st.session_state:
    st.session_state.key_phrases = None


# ============================================================
# HEADER
# ============================================================

st.write("")

left, center, right = st.columns([1, 1.5, 1])

with center:

    st.markdown(
        """
        # 🎙️ Lecture Voice-to-Notes
        """,
        unsafe_allow_html=False
    )

    st.markdown(
        "### Turn your lectures into organized study material"
    )

    st.write(
        "Upload your lecture recording and let Azure AI "
        "transform your speech into a transcript, summary, "
        "and key concepts."
    )

st.write("")


# ============================================================
# FEATURE INDICATORS
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.info(
        "🎧 **Speech Recognition**\n\nAzure AI Speech"
    )


with c2:

    st.success(
        "📌 **Smart Summary**\n\nAzure AI Language"
    )


with c3:

    st.warning(
        "🔑 **Key Concepts**\n\nAI-powered extraction"
    )


st.divider()


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<h2 class="center-heading">📁 Upload Your Lecture</h2>',
    unsafe_allow_html=True
)


with st.container(border=True):

    st.subheader("Choose your lecture recording")

    st.caption(
        "Supported format: WAV • Maximum file size depends "
        "on your Streamlit configuration."
    )

    uploaded_file = st.file_uploader(
        "Drag and drop your WAV file here",
        type=["wav"],
        help="Upload a WAV recording of your lecture.",
        label_visibility="visible"
    )


# ============================================================
# FILE PREVIEW
# ============================================================

if uploaded_file is not None:

    st.write("")

    with st.container(border=True):

        st.markdown(
            '<h3 class="center-heading">🎵 Lecture Preview</h3>',
            unsafe_allow_html=True
        )

        st.audio(
            uploaded_file,
            format="audio/wav"
        )

        file_size = uploaded_file.size / (1024 * 1024)

        info1, info2, info3 = st.columns([3, 1, 1])

        with info1:

            st.caption("📄 File Name")
            st.caption(uploaded_file.name)


        with info2:

            st.caption("💾 Size")
            st.caption(f"{file_size:.2f} MB")


        with info3:

            st.caption("🎵 Format")
            st.caption("WAV")


    st.write("")


    # ========================================================
    # GENERATE BUTTON
    # ========================================================

    generate_col1, generate_col2, generate_col3 = st.columns(
        [1, 2, 1]
    )

    with generate_col2:

        generate_button = st.button(
            "✨ Generate Lecture Notes",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # PROCESS AUDIO
    # ========================================================

    if generate_button:

        audio_path = None

        try:

            with st.status(
                "🤖 AI is processing your lecture...",
                expanded=True
            ):

                # ------------------------------------------------
                # SAVE AUDIO
                # ------------------------------------------------

                st.write(
                    "🎧 Preparing your audio..."
                )

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                ) as temp_audio:

                    temp_audio.write(
                        uploaded_file.getvalue()
                    )

                    temp_audio.flush()

                    audio_path = temp_audio.name


                # ------------------------------------------------
                # TRANSCRIPTION
                # ------------------------------------------------

                st.write(
                    "🗣️ Converting speech into text..."
                )

                transcript = transcribe_audio(
                    audio_path
                )


                # ------------------------------------------------
                # SUMMARY
                # ------------------------------------------------

                st.write(
                    "📌 Creating your lecture summary..."
                )

                summary = generate_summary(
                    transcript
                )


                # ------------------------------------------------
                # KEY PHRASES
                # ------------------------------------------------

                st.write(
                    "🔑 Finding important concepts..."
                )

                key_phrases = extract_key_phrases(
                    transcript
                )


                # ------------------------------------------------
                # SAVE RESULTS
                # ------------------------------------------------

                st.session_state.transcript = transcript
                st.session_state.summary = summary
                st.session_state.key_phrases = key_phrases

                st.write(
                    "✅ Your study material is ready!"
                )


            # ------------------------------------------------
            # DELETE TEMPORARY FILE
            # ------------------------------------------------

            if audio_path and os.path.exists(audio_path):

                os.remove(audio_path)

            audio_path = None


            st.success(
                "🎉 Lecture processed successfully!"
            )


        except Exception as e:

            if audio_path and os.path.exists(audio_path):

                os.remove(audio_path)

            st.error(
                f"❌ Something went wrong: {e}"
            )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.transcript:

    st.divider()


    # ========================================================
    # STUDY MATERIAL HEADING
    # ========================================================

    st.markdown(
        '<h2 class="center-heading">📚 Your Study Material</h2>',
        unsafe_allow_html=True
    )

    st.caption(
        "AI-generated learning material based on your lecture."
    )


    transcript = st.session_state.transcript
    summary = st.session_state.summary
    key_phrases = st.session_state.key_phrases


    # ========================================================
    # STATISTICS
    # ========================================================

    st.subheader("📊 Lecture Overview")

    summary_count = len(summary)
    concept_count = len(key_phrases)
    word_count = len(transcript.split())


    stat1, stat2, stat3 = st.columns(3)


    # --------------------------------------------------------
    # SUMMARY POINTS
    # --------------------------------------------------------

    with stat1:

        with st.container(border=True):

            st.metric(
                label="📌 Summary Points",
                value=summary_count
            )

            st.caption(
                "Important points identified"
            )


    # --------------------------------------------------------
    # KEY CONCEPTS
    # --------------------------------------------------------

    with stat2:

        with st.container(border=True):

            st.metric(
                label="🔑 Key Concepts",
                value=concept_count
            )

            st.caption(
                "Important concepts extracted"
            )


    # --------------------------------------------------------
    # TRANSCRIPT WORDS
    # --------------------------------------------------------

    with stat3:

        with st.container(border=True):

            st.metric(
                label="📝 Transcript Words",
                value=word_count
            )

            st.caption(
                "Total words detected"
            )


    st.write("")


    # ========================================================
    # TABS
    # ========================================================

    summary_tab, concepts_tab, transcript_tab = st.tabs(
        [
            "📌 Summary",
            "🔑 Key Concepts",
            "📝 Transcript"
        ]
    )


    # ========================================================
    # SUMMARY TAB
    # ========================================================

    with summary_tab:

        st.markdown(
            '<h3 class="center-heading">📌 Lecture Summary</h3>',
            unsafe_allow_html=True
        )


        if summary:

            for index, sentence in enumerate(
                summary,
                start=1
            ):

                with st.container(border=True):

                    st.info(
                        f"**{index}.** {sentence}"
                    )


        else:

            st.warning(
                "No summary points were generated."
            )


    # ========================================================
    # KEY CONCEPTS TAB
    # ========================================================

    with concepts_tab:

        st.markdown(
            '<h3 class="center-heading">🔑 Key Concepts</h3>',
            unsafe_allow_html=True
        )

        st.write(
            "Important terms and concepts identified "
            "from your lecture."
        )


        if key_phrases:

            concept_columns = st.columns(3)


            for index, phrase in enumerate(
                key_phrases
            ):

                with concept_columns[
                    index % 3
                ]:

                    with st.container(border=True):

                        st.success(
                            f"🔹 {phrase}"
                        )


        else:

            st.warning(
                "No key concepts were identified."
            )


    # ========================================================
    # TRANSCRIPT TAB
    # ========================================================

    with transcript_tab:

        st.markdown(
            '<h3 class="center-heading">📝 Full Lecture Transcript</h3>',
            unsafe_allow_html=True
        )

        st.caption(
            "Review or copy the complete transcription "
            "generated from your lecture."
        )


        st.text_area(
            "Transcript",
            value=transcript,
            height=450,
            label_visibility="collapsed"
        )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.divider()


    st.markdown(
        '<h3 class="center-heading">💾 Export Your Notes</h3>',
        unsafe_allow_html=True
    )


    summary_text = "\n".join(
        f"{i}. {sentence}"
        for i, sentence in enumerate(
            summary,
            start=1
        )
    )


    concepts_text = "\n".join(
        f"- {phrase}"
        for phrase in key_phrases
    )


    notes_text = f"""
# LECTURE VOICE-TO-NOTES

## LECTURE SUMMARY

{summary_text}

## KEY CONCEPTS

{concepts_text}

## FULL TRANSCRIPT

{transcript}
"""


    download1, download2, download3 = st.columns(
        [1, 2, 1]
    )


    with download2:

        st.download_button(
            label="⬇️ Download Study Notes",
            data=notes_text,
            file_name="lecture_notes.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.write("")

st.divider()


st.markdown(
    """
    <div class="center-footer">
        🎙️ Lecture Voice-to-Notes •
        Powered by Azure AI Speech & Azure AI Language
    </div>
    """,
    unsafe_allow_html=True
)