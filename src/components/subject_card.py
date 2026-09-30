import streamlit as st

def subject_card(name, code, section, stats=None, footer_callback=None, footer_label=None):
    html = f"""
    <div style="background:white; border-left: 8px solid #EB459E; padding:20px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom:15px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
        <h3 style="margin:0; color: #1e293b; font-size: 1.35rem;">{name}</h3>
        <p style="color:#64748b; margin:8px 0;">Code : <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:6px; font-weight:600;">{code}</span> | Section : <b>{section}</b></p>
    """
    
    if stats:
        html += '<div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">'
        for item in stats:
            if isinstance(item, dict):
                icon = item.get("icon", "")
                value = item.get("value", "")
                label = item.get("label", "")
            elif isinstance(item, (list, tuple)):
                if len(item) == 3:
                    icon, label, value = item
                elif len(item) == 2:
                    icon, value = item
                    label = ""
                else:
                    icon, label, value = "", "", str(item)
            else:
                icon, label, value = "", "", str(item)
            
            label_text = f" {label}" if label else ""
            html += f'<div style="background: #EB459E15; color:#1e293b; padding:5px 12px; border-radius:12px; font-size:0.88rem;">{icon} <b>{value}</b>{label_text}</div>'
        
        html += "</div>"
    
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()