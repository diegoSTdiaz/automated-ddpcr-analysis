import pandas as pd
import streamlit as st

def create_plate_df(plate_layout_df, study_info_df, default_ng, user_overrides):
    wells = [f"{r}{c}" for r in "ABCDEFGH" for c in range(1,13)]
    plate = pd.DataFrame({"Well": wells, "Sample": "", "DNA_ng": default_ng})

    if plate_layout_df is not None and {"Well", "Sample"}.issubset(plate_layout_df.columns):
        layout = plate_layout_df[["Well", "Sample"]].copy()
        layout["Well"] = layout["Well"].astype(str).str.upper()
        plate = plate.merge(layout, on="Well", how="left", suffixes=("", "_new"))
        plate["Sample"] = plate["Sample_new"].combine_first(plate["Sample"])
        plate.drop(columns=[c for c in plate.columns if "_new" in c], errors="ignore", inplace=True)

    if study_info_df is not None and {"Sample", "DNA_ng"}.issubset(study_info_df.columns):
        study_dict = dict(zip(study_info_df["Sample"], study_info_df["DNA_ng"]))
        plate["DNA_ng"] = plate["Sample"].map(study_dict).fillna(plate["DNA_ng"])

    for well, ng in user_overrides.items():
        if well.upper() in plate["Well"].values:
            plate.loc[plate["Well"] == well.upper(), "DNA_ng"] = float(ng)

    return plate


def render_interactive_plate(plate_df, current_overrides):
    new = current_overrides.copy()
    cols = st.columns(13)
    cols[0].markdown("**Row**")
    for i in range(1,13): cols[i].markdown(f"**{i}**")

    for row in "ABCDEFGH":
        cols = st.columns(13)
        cols[0].markdown(f"**{row}**")
        for col in range(1,13):
            well = f"{row}{col}"
            r = plate_df[plate_df["Well"] == well].iloc[0]
            sample = str(r["Sample"]) if pd.notna(r["Sample"]) and r["Sample"] != "" else "—"
            ng = float(r["DNA_ng"])
            color = "#ff9d76" if well in current_overrides else "#a8e6cf" if ng == 140 else "#ffb3b3" if ng < 50 else "#d4e6f1"

            with cols[col]:
                if st.button(f"{sample}\n{ng:.0f} ng", key=well):
                    val = st.number_input("DNA ng", value=ng, step=5.0, key=f"in_{well}")
                    new[well] = val
                    st.rerun()
    return new
