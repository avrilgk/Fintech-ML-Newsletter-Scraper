import streamlit as st
from crypto_web_scraping import *
from newsletter_process_to_word import *
from io import BytesIO

st.title("Step 1: Scrape Article")

pub_date = st.text_input("Enter publish date (e.g. 1 Mar 2024)")
earliest_date = st.text_input("Enter earliest date of articles (e.g. 25 Feb 2024)")

def retrieve_curated_news(pub_date, earliest_date):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df, _ = generate_curated_news(pub_date, earliest_date)
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data


if st.button('Submit'):
    data = retrieve_curated_news(pub_date,earliest_date)
    st.download_button(label='Download Excel File', 
                       data=data,
                       file_name=f'scraped_news_headlines_{pub_date}.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

st.title("Step 2: Generate Newsletter")

newsletter_doc_title = st.text_input("Enter title for newsletter document")
pub_date1 = st.text_input("Enter publish date (e.g. 1 Mar 2024)", key=1231243)
uploaded_file = st.file_uploader("Upload Excel", type=['xlsx'])

if uploaded_file is not None:
    # Read the Excel file into a Pandas dataframe
    doc = write_newsletter(uploaded_file, pub_date1)
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    st.download_button(label="Download Newsletter Document",
                       data=file_stream,
                       file_name=f'{newsletter_doc_title}.docx',
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")