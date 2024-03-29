import streamlit as st
from web_scraping import *
from newsletter_process_to_word import *
from io import BytesIO
import datetime

def format_date(d):
    return d.strftime("%d %b %Y")

def get_curated_news_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

def get_curated_news_df(df):
    df.insert(0,'selected',False)
    return df

def get_cleaned_edited_df(edited_df, top_1_headline, top_2_headline):
    edited_df = edited_df[edited_df['selected']]
    for headline in [top_2_headline, top_1_headline]:

        row = edited_df[edited_df['title'] == headline]

        # Remove the row from the original DataFrame
        edited_df = edited_df[edited_df['title'] != headline]

        # Concatenate the row at the beginning of the DataFrame
        edited_df = pd.concat([row, edited_df]).reset_index(drop=True)
    
    return edited_df

def get_options(df):
    options = df[df['selected']]['title'].tolist()
    return options

st.session_state.password = st.text_input("Password", type="password")

if st.session_state.password == "fintechml":
    logged_in = True
    st.title("Step 1: Scrape Article")
    pub_date = st.date_input("Enter publish date", datetime.date.today())
    earliest_date = st.date_input("Enter earliest date of articles", datetime.date.today() - datetime.timedelta(days=6))

    if 'curated_news_df' not in st.session_state:
        st.session_state.curated_news_df = None

    edited_df = None
    top_1_headline = None
    top_2_headline = None

    if st.button('Submit'):
        df,_ = generate_curated_news(format_date(pub_date), format_date(earliest_date))
        st.session_state.curated_news_df = get_curated_news_df(df)

    if st.session_state.curated_news_df is not None:
        edited_df = st.data_editor(st.session_state.curated_news_df, hide_index=True)
        options = get_options(edited_df)
        st.write(f'selected **{len(options)}** articles')
        st.info('Table is editable', icon="ℹ️")
        top_1_headline = st.selectbox('Choose 1st top headline', options)
        top_2_headline = st.selectbox('Choose 2nd top headline', options)
        
        if top_1_headline == top_2_headline:
            # Display an error message
            st.error('Error: The two selected options must be different.')
        else:
            # Display the selected options if they are different
            st.success(f'You selected "{top_1_headline}" and "{top_2_headline}".')
        
    st.title("Step 2: Generate Newsletter")
    newsletter_doc_title = st.text_input("Enter title for newsletter document")
    cleaned_edited_df = get_cleaned_edited_df(edited_df,top_1_headline, top_2_headline)
    doc = write_newsletter_from_df(cleaned_edited_df, format_date(pub_date))
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    st.download_button(label="Download Newsletter Document",
                    data=file_stream,
                    file_name=f'{newsletter_doc_title}.docx',
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
