from datetime import timedelta

def calculate_baseline_date_range(go_live_date):
    end_date = go_live_date - timedelta(weeks=2)
    start_date = end_date - timedelta(weeks=12) + timedelta(days=1)

    return {"start_date": start_date, "end_date": end_date}

def calculate_pre_cutover_date_range(go_live_date):
    end_date = go_live_date + timedelta(weeks=1)
    start_date = end_date - timedelta(weeks=3) + timedelta(days=1)

    return {"start_date": start_date, "end_date": end_date}



def calculate_post_cutover_date_range(go_live_date):
    end_date = go_live_date + timedelta(weeks=2)
    start_date = end_date - timedelta(weeks=3) + timedelta(days=1)

    return {"start_date": start_date, "end_date": end_date}

