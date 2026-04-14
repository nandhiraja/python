

def generate_report(current_data:dict, previous_data:dict):

    new_price_items = []
    
    for key, value in current_data.items():
        current = value
        previous = previous_data[key]
        if(is_changed(current, previous)):
            new_price_items.append({'name':current['name'],'old_price':previous['price'],'new_price':current['price']}) 

    return new_price_items


def is_changed(data_1,data_2):

    if(data_1['price'] != data_2['price']):
        #  print(data_1['name'],"  -------- ",data_2['name'] ,'\n\n')
         return True
    


