def calculate_copies_per_sample(qx_data, plate_df):
    plate_dict = plate_df.set_index("Well")[["Sample", "DNA_ng"]].to_dict("index")
    results = []

    for _, row in qx_data.iterrows():
        well = row["Well"].upper()
        if well not in plate_dict or plate_dict[well]["Sample"] == "":
            continue
        sample = plate_dict[well]["Sample"]
        ng = plate_dict[well]["DNA_ng"]
        copies_ul = row["Copies/µL"]
        copies_ng = copies_ul / ng if ng > 0 else 0

        results.append({
            "Well": well,
            "Sample": sample,
            "Target": row.get("Target", ""),
            "Copies/µL": copies_ul,
            "DNA_ng": ng,
            "Copies/ng": round(copies_ng, 3)
        })

    return pd.DataFrame(results)
