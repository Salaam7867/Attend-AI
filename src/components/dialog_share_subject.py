
import streamlit as st


@st.dialog("Share Class Link")
def share_subject_dialog(subject):
    import qrcode
    import io

    # Generate the join link
    app_domain = "attend-ai.streamlit.app"  # Change this to your actual domain when deployed
    join_link = f"http://{app_domain}/?subject_code={subject['subject_code']}"

    st.subheader("Scan to Join")
    
    col1, col2 = st.columns(2)

    with col1:
        
        st.markdown("**Copy Link**")
        st.code(join_link)
        st.code(subject['subject_code'])
        if st.button("Copy this link to share on Whatsapp or Email", type='secondary'):
            st.write(join_link)

    with col2:
        # Generate QR code
        qr = qrcode.make(join_link)
        buf = io.BytesIO()
        qr.save(buf)
        buf.seek(0)
        st.image(buf, caption="QRCODE for class joining")