import tkinter as tk #for GUI
from tkinter import messagebox
from datetime import datetime
from bs4 import BeautifulSoup #parsing HTML
import requests #Request fetch data from web
import pandas as pd #handiling data
import csv


# Create dictionary for cities and city_codes
#storage req-1  utilize data structure such as list dictionary

cities = {
    "Rome": "-126693",
    "Madrid": "-390625",
    "Prague": "-553173",
    "Vienna": "-1995499",
    "Amsterdam": "-2140479",
    "Barcelona": "-372490",
    "Berlin": "-1746443",
    "London": "-2601889",
    "Paris": "-1456928",
    "Budapest": "850553"
}

top_hotels_data = []  # Define as a global variable

def validate_dates():
    try:
        check_in_date = check_in_entry.get()
        check_out_date = check_out_entry.get()
        today = datetime.now().strftime("%Y-%m-%d")

        if check_in_date < today or check_out_date < today:
            messagebox.showwarning("Invalid Date", "Check-in or check-out date cannot be in the past.")
            return False

        if check_in_date >= check_out_date:
            messagebox.showwarning("Invalid Date", "Check-in date should be before check-out date. Please select again.")
            return False

        return True

    except ValueError:
        messagebox.showwarning("Invalid Date", "Please select the dates correctly.")
        return False

def get_dates():
    if validate_dates():
        print("selected city:", selected_city.get())
        print("check in date:", check_in_entry.get())
        print("check out date:", check_out_entry.get())
        print("selected currency:", currency.get())

def fetch_hotels(city, check_in, check_out, currency):
    global top_hotels_data  # Access the global variable

    try:
        url = get_url(city, check_in, check_out)
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        hotels = soup.findAll('div', {'data-testid': 'property-card'})

        top_hotels_data = []  # Clear existing data

        for hotel in hotels:
            # add hotel name
            name_element = hotel.find('div', {'data-testid': 'title'})
            name = name_element.text.strip()
            # Extract the hotel address
            address_element = hotel.find('span', {'data-testid': 'address'})
            address = address_element.text.strip() if address_element else None
            # add distance
            distance_element = hotel.find('span', {'data-testid': 'distance'})
            distance = distance_element.text.strip() if distance_element else None
            # add rating
            rating_element = hotel.find('span', {'class': 'a3332d346a'})
            rating = rating_element.text.strip() if rating_element else None
            # add hotel price
            price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
            price_str = price_element.text.strip() if price_element else "NOT GIVEN"

            # Extract numerical value from price string
            price_value = price_str.split()[1].replace(',', '')  # Remove commas
            price = float(price_value)

            # Convert price to the selected currency
            if currency == 'EURO':
                price /= 30  # Convert to EURO from TL

            #otel bilgileri
            top_hotels_data.append({
                'title': name,
                'address': address if address else "Address not available",
                'distance': distance if distance else "Distance not available",
                'rating': rating if rating else "Rating not available",
                'price': price if price else "NOT GIVEN"
            })

            # loop 5 otelde durduran
            if len(top_hotels_data) >= 5:
                break
        #data kaydetme kısmı
        hotels = pd.DataFrame(top_hotels_data)
        hotels.head()
        hotels.to_csv('test_hotels.csv', header=True, index=False)

        # sort by order
        top_hotels_data.sort(key=lambda x: x['price'])

        # Display top hotels
        display_top_hotels()

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred while fetching hotel information: {str(e)}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching hotel information: {str(e)}")

def display_top_hotels():
    top_hotels_text.delete(1.0, tk.END)  # Clear existing text

    for index, hotel in enumerate(top_hotels_data, start=1):
        if index > 5:  # Display only the top 5 hotels
            break

        hotel_info = f"{index}. {hotel['title']}\nAddress: {hotel['address']}\nDistance: {hotel['distance']}\nRating: {hotel['rating']}\nPrice: {hotel['price']}\n\n"
        top_hotels_text.insert(tk.END, hotel_info)

def get_url(city, check_in, check_out):
    city_id = cities.get(city, "")
    base_url = 'https://www.booking.com/searchresults.html?ss={city}&ssne={city}&ssne_untouched={city}&efdco=1&label=gen173nr-1FCAEoggI46AdIM1gEaOQBiAEBmAExuAEHyAEP2AEB6AEBAECiAIBqAIDuAKo8sKxBsACAdICJGZlZWVmNGJjLWI2OGEtNGM0OS05ODk0LTM2ZGQ4YzkxYzY0MNgCBeACAQ&aid=304142&lang=en-us&sb=1&src_elem=sb&src=index&dest_id={city_id}&dest_type=city&checkin={check_in}&checkout={check_out}&group_adults=2&no_rooms=1&group_children=0'
    return base_url.format(city=city, city_id=city_id, check_in=check_in, check_out=check_out)


#GUI PART

root = tk.Tk()
root.title("BEST HOTEL FOR YOU")

image = tk.PhotoImage(file="/Users/silacetinkaya/Desktop/hotel.png")
image = image.subsample(2, 2)  # 0.5 KÜÇÜLT
label = tk.Label(root, image=image)
#Resmi ekranda gösterin
label.pack()
# Şehir seçimi için dropdown menü
label = tk.Label(root, text="select city :",foreground="pink")
label.pack()

european_cities = [
    "Amsterdam", "Barcelona", "Berlin",     "London",
    "Paris", "Rome", "Vienna", "Madrid", "Prague", "Budapest"
]
selected_city = tk.StringVar(root)
selected_city.set(european_cities[0])

city_menu = tk.OptionMenu(root, selected_city, *european_cities)
city_menu.pack()

# Giriş ve çıkış tarihleri için giriş kutuları
check_in_label = tk.Label(root, text="check-in date (yyyy-aa-gg):",foreground="pink")
check_in_label.pack()
check_in_entry = tk.Entry(root)
check_in_entry.pack()

check_out_label = tk.Label(root, text="check-out date (yyyy-aa-gg):",foreground="pink")
check_out_label.pack()
check_out_entry = tk.Entry(root)
check_out_entry.pack()
# Para birimi seçimi için radyo düğmeleri
currency_label = tk.Label(root, text="Currency:", foreground="pink")
currency_label.pack()

currency = tk.StringVar()
currency.set("TL")  # Default selection

euro_radio_button = tk.Radiobutton(root, text="EURO", variable=currency, value="EURO")
euro_radio_button.pack()

tl_radio_button = tk.Radiobutton(root, text="TL", variable=currency, value="TL")
tl_radio_button.pack()
# Tarihleri kaydetmek için buton
submit_button = tk.Button(root, text="save dates", command=get_dates)
submit_button.pack()

# En iyi 5 otel
title_label = tk.Label(root, text="Best 5 hotel", font=("Helvetica", 16, "bold"),foreground="pink")
title_label.pack()

# En iyi 5 oteli göstermek için metin alanı
top_hotels_text = tk.Text(root, height=15, width=60)
top_hotels_text.pack()

# Otelleri göstermek için buton
display_button = tk.Button(root, text="Show Top Hotels", command=lambda: fetch_hotels(selected_city.get(), check_in_entry.get(), check_out_entry.get(), currency.get()))
display_button.pack()

root.mainloop()


