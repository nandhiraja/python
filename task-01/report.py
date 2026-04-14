from datetime import datetime


def generate_report(current_data:dict, previous_data:dict):

    new_price_items = []

    for key, value in current_data.items():
        current = value 
        previous = previous_data.get(key)
        if(previous and is_changed(current, previous)):
            new_price_items.append({'name':current['name'],'old_price':previous['price'],'new_price':current['price']}) 

    if(len(new_price_items)!=0):
        create_csv(new_price_items)
        return 'Price changed report generated'
    
    return 'No price changed'


def is_changed(data_1,data_2):

    if not data_2:
        return False 
    return data_1['price'] != data_2['price']
    

def create_csv(items):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f'./reports/Report-{timestamp}.csv'
    print(path)
    with open (path,'w') as report:
        report.write("item_name , old_price , new_price\n")
        
        for item in items:
            line = f"{item['name']} , {item['old_price']} , {item['new_price']}\n"
            report.write(line)


