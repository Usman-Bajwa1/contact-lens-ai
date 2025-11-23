import streamlit as st
import asyncio
from app.services.google_llm import Googlellm
from app.services.manager import ContactManager
from app.schema.app_schemas import ContactCreate, DuplicateCheckResult
from streamlit_agraph import agraph, Node, Edge, Config


st.set_page_config(page_title="ContactLens AI", page_icon="📇", layout="wide")


ContactManager.init_state()
if "current_extraction" not in st.session_state:
    st.session_state.current_extraction = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None


with st.sidebar:
    st.title("📇 ContactLens AI")
    st.caption("Powered by Gemini 2.5 Pro")
    st.markdown("---")
    
    st.write("### ⚙️ Settings")
    mask_pii = st.toggle("🔒 Privacy Mode", value=False)
    
    st.write("### 🧠 AI Features")
    st.markdown("""
    - **Vision Extraction**: Images to JSON
    - **Semantic Deduplication**: LLM checks for duplicates
    - **Enrichment**: Infers skills & socials
    - **Network Graph**: Visualizes connections
    """)


tab_upload, tab_list, tab_graph = st.tabs(["📤 Upload & Extract", "📋 Contact List", "🕸️ Network Graph"])

with tab_upload:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Upload Image")
        
        uploaded_file = st.file_uploader("Upload Business Card", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            if st.session_state.last_uploaded_file != uploaded_file.name:
                st.session_state.current_extraction = None
                st.session_state.last_uploaded_file = uploaded_file.name
            
            st.image(uploaded_file, caption="Card Preview", width=400)
            st.markdown("---")
            
            if st.button("✨ Extract Info via AI", type="primary", use_container_width=True):
                with st.spinner("🔍 Analyzing text & logos with Gemini Vision..."):
                    try:
                        llm = Googlellm()
                        image_bytes = uploaded_file.getvalue()
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(llm.get_contact_info(image_bytes))
                        
                        if hasattr(result, "model_dump"):
                            st.session_state.current_extraction = result.model_dump()
                        else:
                            st.session_state.current_extraction = result
                        
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Extraction Error: {e}")

    with col2:
        st.subheader("2. Review & Save")
        
        if st.session_state.current_extraction:
            st.success("✅ Extraction Complete!")
            
            raw_data = st.session_state.current_extraction
            if isinstance(raw_data, dict):
                data = ContactCreate(**raw_data)
            else:
                data = raw_data
            
            score = data.confidence_score
            st.progress(score, text=f"AI Confidence Score: {int(score*100)}%")

            with st.form("edit_form"):
                c_name = st.text_input("Full Name", value=data.full_name)
                c_company = st.text_input("Company", value=data.company)
                c_job = st.text_input("Job Title", value=data.job_title)
                c_email = st.text_input("Email", value=data.email)
                c_phone = st.text_input("Phone", value=data.phone)
                skills_str = ", ".join(data.skills) if data.skills else ""
                c_skills = st.text_input("Skills (Inferred)", value=skills_str)
                c_summary = st.text_area("AI Summary", value=data.summary, height=100)
                
                if data.social_media:
                    st.info(f"🌍 Found Socials: {data.social_media}")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    submitted = st.form_submit_button("💾 Save to List", type="primary")
                with col_b2:
                    improved = st.form_submit_button("🪄 AI Auto-Improve")

                if improved:
                    with st.spinner("AI is normalizing data..."):
                        current_dict = data.model_dump()
                        current_dict.update({
                            "full_name": c_name, "company": c_company, 
                            "job_title": c_job, "email": c_email, "phone": c_phone
                        })
                        
                        llm = Googlellm()
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        improved_data = loop.run_until_complete(llm.improve_contact_data(current_dict))
                        
                        if hasattr(improved_data, "model_dump"):
                            st.session_state.current_extraction = improved_data.model_dump()
                        else:
                            st.session_state.current_extraction = improved_data
                        st.rerun()

                if submitted:
                    with st.spinner("Checking for semantic duplicates..."):
                        final_skills = [s.strip() for s in c_skills.split(",")] if c_skills else []
                        
                        final_contact = ContactCreate(
                            full_name=c_name, company=c_company, job_title=c_job,
                            email=c_email, phone=c_phone, summary=c_summary,
                            tags=data.tags, confidence_score=data.confidence_score,
                            address=data.address, skills=final_skills,
                            social_media=data.social_media
                        )

                        llm = Googlellm()
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        existing_contacts = ContactManager.get_all_contacts()
                        dup_check_raw = loop.run_until_complete(
                            llm.check_duplicate_semantic(final_contact.model_dump(), existing_contacts)
                        )
                        
                        if isinstance(dup_check_raw, dict):
                            dup_check = DuplicateCheckResult(**dup_check_raw)
                        else:
                            dup_check = dup_check_raw
                        
                        ContactManager.add_contact(final_contact, is_dup=dup_check.is_duplicate, dup_reason=dup_check.reason)
                        
                        if dup_check.is_duplicate:
                            st.toast(f"⚠️ Flagged as Duplicate: {dup_check.reason}", icon="⚠️")
                        else:
                            st.toast("Contact Saved Successfully!", icon="✅")
                        
                        st.session_state.current_extraction = None
                        st.rerun()
        
        elif uploaded_file is not None:
            st.info("👆 **Image Ready!**\n\nPlease click the **'Extract Info via AI'** button on the left to process this card.")
        else:
            st.warning("👈 Please upload an image to begin.")

with tab_list:
    st.subheader("📋 Intelligent Contact List")
    
    df = ContactManager.get_all_as_df(mask_pii=mask_pii)
    
    if not df.empty:
        st.dataframe(
            df,
            column_config={
                "is_duplicate": st.column_config.CheckboxColumn("⚠️ Duplicate", disabled=True),
                "duplicate_reason": st.column_config.TextColumn("Duplicate Reason"),
                "social_media": st.column_config.TextColumn("Socials"),
                "confidence_score": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1)
            },
            width="stretch",
            hide_index=True
        )
        
        dup_count = df['is_duplicate'].sum()
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Contacts", len(df))
        col_m2.metric("Duplicates Flagged", int(dup_count), delta_color="inverse")
    else:
        st.info("No contacts yet. Upload a card to get started!")

with tab_graph:
    st.subheader("🕸️ Network Connections")
    st.caption("Visualizing relationships by Company and Industry")
    
    contacts = ContactManager.get_all_contacts()
    
    if contacts:
        nodes = []
        edges = []
        companies = set()
        
        for contact in contacts:
            c_id = contact.get('id')
            c_name = contact.get('full_name', 'Unknown')
            c_comp = contact.get('company')
            c_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png" 

            nodes.append(Node(
                id=c_id, 
                label=c_name, 
                size=25, 
                shape="circularImage",
                image=c_img,
                title=f"{contact.get('job_title')} @ {c_comp}" 
            ))
            
            if c_comp:
                clean_comp = c_comp.strip()
                companies.add(clean_comp)
                edges.append(Edge(source=c_id, target=clean_comp, color="#dfe4ea"))
        
        for comp in companies:
            nodes.append(Node(
                id=comp, 
                label=comp, 
                size=35, 
                shape="circularImage",
                image="https://cdn-icons-png.flaticon.com/512/4400/4400465.png", 
                color="#f1f2f6"
            ))

        config = Config(
            width="100%",
            height=600,
            directed=False, 
            physics=True, 
            hierarchical=False,
            nodeHighlightBehavior=True, 
            highlightColor="#F7A557",
            collapsible=False
        )

        return_value = agraph(nodes=nodes, edges=edges, config=config)
    
    else:
        st.info("Add some contacts to visualize your network graph!")