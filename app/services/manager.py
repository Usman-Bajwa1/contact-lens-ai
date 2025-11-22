import streamlit as st
import uuid
import pandas as pd
from app.schema.app_schemas import ContactResponse, ContactCreate
from app.utils.utils import mask_email, mask_phone

class ContactManager:
    @staticmethod
    def init_state():
        if "contacts" not in st.session_state:
            st.session_state.contacts = []

    @staticmethod
    def get_all_contacts():
        return st.session_state.contacts

    @staticmethod
    def add_contact(contact: ContactCreate, is_dup: bool, dup_reason: str = None):
        new_entry = ContactResponse(
            id=str(uuid.uuid4()),
            is_duplicate=is_dup,
            duplicate_reason=dup_reason,
            **contact.model_dump()
        )
        st.session_state.contacts.append(new_entry.model_dump())
        return new_entry

    @staticmethod
    def get_all_as_df(mask_pii: bool = False):
        if not st.session_state.contacts:
            return pd.DataFrame()
        
        df = pd.DataFrame(st.session_state.contacts)
        
        if mask_pii:
            if 'email' in df.columns:
                df['email'] = df['email'].apply(mask_email)
            if 'phone' in df.columns:
                df['phone'] = df['phone'].apply(mask_phone)
                
        return df