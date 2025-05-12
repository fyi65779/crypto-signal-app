# updatedallcoin.py (Streamlit-compatible version — CLI preserved)
import streamlit as st
import requests
import time

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def fetch_top_coins(limit=30):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': limit,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        coins = response.json()

        if not any(c['symbol'].lower() == 'trump' for c in coins):
            trump = fetch_specific_coin("official-trump")
            if trump:
                coins.append(trump)

        if not any(c['symbol'].lower() == 'zerebro' for c in coins):
            zerebro = fetch_specific_coin("zerebro")
            if zerebro:
                coins.append(zerebro)

        return coins
    except Exception as e:
        print(f"❌ Error fetching coins: {e}")
        return []

def fetch_specific_coin(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            'id': data['id'],
            'symbol': data['symbol'],
            'current_price': data['market_data']['current_price']['usd'],
            'price_change_percentage_1h_in_currency': data['market_data']['price_change_percentage_1h_in_currency']['usd'],
            'price_change_percentage_24h_in_currency': data['market_data']['price_change_percentage_24h_in_currency']['usd']
        }
    except Exception as e:
        print(f"❌ Error fetching {coin_id}: {e}")
        return None

def generate_signal(coin):
    price = coin['current_price']
    change_1h = coin.get('price_change_percentage_1h_in_currency', 0)
    change_24h = coin.get('price_change_percentage_24h_in_currency', 0)

    momentum = 'Bullish 🔼' if change_1h > 0 and change_24h > 0 else 'Bearish 🔽' if change_1h < 0 and change_24h < 0 else 'Mixed ⚖️'
    direction = '📈 Buy (Long)' if change_24h > 0 else '📉 Sell (Short)'
    confidence = min(max((abs(change_1h) + abs(change_24h)) * 1.5, 10), 95)

    expected_change = change_24h / 100
    predicted_move = round(price * expected_change, 2)
    profitability = '✅ High chance of profit' if abs(predicted_move) > 5 else '⚠️ Profit < $5'
    prediction = '🚀 Likely to go up' if change_24h > 0 else '📉 May go down'

    up_prob = min(60 + change_24h, 85) if change_24h > 0 else 20
    down_prob = 100 - up_prob

    max_up = round(price * (1 + abs(change_24h / 100)), 4)
    max_down = round(price * (1 - abs(change_24h / 100)), 4)
    only_max = f"🔼 Max Up Prediction: ${max_up}" if up_prob > down_prob else f"🔽 Max Down Prediction: ${max_down}"

    return {
        'symbol': coin['symbol'].upper(),
        'id': coin['id'],
        'direction': direction,
        'entry_point': round(price, 4),
        'confidence': round(confidence, 2),
        'prediction': prediction,
        'profitability': profitability,
        'up_probability': round(up_prob),
        'down_probability': round(down_prob),
        'only_max': only_max,
        'momentum': momentum
    }

def track_price(coin, entry_point):
    previous_price = coin['current_price']
    while True:
        time.sleep(60)
        coin_data = fetch_coin_by_id(coin['id'])
        if not coin_data:
            print("❌ Error fetching live coin data.")
            break

        price = coin_data['market_data']['current_price']['usd']
        change_24h = coin_data['market_data'].get('price_change_percentage_24h_in_currency', {}).get('usd', 0)

        price_diff = round(price - entry_point, 2)
        diff_percent = round((price_diff / entry_point) * 100, 2)

        price_trend = "🟢" if price > previous_price else "🔴" if price < previous_price else "📍"
        situation = "✅ Situation is improving." if change_24h > 0 else "❌ Situation is worsening."

        print(f"\n⏱️ 1 Minute Update:")
        print(f"Current Price: ${price}")
        print(f"Change from Entry: ${price_diff} ({diff_percent}%)")
        print(f"Price Trend: {price_trend}")
        print(situation)

        if price_diff < 0:
            print("⚠️ Price is dropping, consider closing your position.")

        previous_price = price

def fetch_coin_by_id(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except:
        return None

def cli_main():
    if not is_connected():
        print("❌ No internet connection.")
        return

    while True:
        coins = fetch_top_coins()
        if not coins:
            print("❌ Unable to fetch coin data.")
            return

        print("\n📊 Available Coins (Top 30 + TRUMP + ZEREBRO):")
        for i, c in enumerate(coins, 1):
            print(f"{i}. {c['symbol'].upper()} - ${c['current_price']}")

        try:
            choice = int(input("\n📥 Select coin number to generate signal: "))
            if choice < 1 or choice > len(coins):
                print("❌ Invalid choice.")
                continue
        except ValueError:
            print("❌ Invalid input.")
            continue

        selected = coins[choice - 1]
        signal = generate_signal(selected)

        print("\n🔔 Signal Generated:")
        print(f"Symbol: {signal['symbol']}")
        print(f"Direction: {signal['direction']}")
        print(f"Entry Point: ${signal['entry_point']}")
        print(f"Confidence: {signal['confidence']}%")
        print(f"Momentum: {signal['momentum']}")
        print(f"Prediction: {signal['prediction']}")
        print(f"Profitability: {signal['profitability']}")
        print(f"Probability of Price Going Up: {signal['up_probability']}%")
        print(f"Probability of Price Going Down: {signal['down_probability']}%")
        print(signal['only_max'])

        track_choice = input("\nWould you like to track the price every 1 minute? (yes/no): ").lower()
        if track_choice == 'yes':
            track_price(selected, signal['entry_point'])
        else:
            print("\n🔄 Returning to coin list...")
            continue

def streamlit_main():
    st.set_page_config(page_title="Crypto Signal Generator", layout="centered")
    st.title("📊 Crypto Signal Generator")

    if not is_connected():
        st.error("🚫 Internet connection nahi hai. Please try again.")
        st.stop()

    if st.button("🔄 Refresh Data"):
        st.experimental_rerun()

    coins = fetch_top_coins()
    coin_names = [f"{c['symbol'].upper()} - ${c['current_price']}" for c in coins if c]

    if not coin_names:
        st.warning("Koi coin data available nahi hai.")
        st.stop()

    selected_index = st.selectbox("Select a coin:", range(len(coin_names)), format_func=lambda x: coin_names[x])
    selected_coin = coins[selected_index]
    signal = generate_signal(selected_coin)

    st.subheader(f"🔔 Signal for {signal['symbol']}")
    st.write(f"**Direction:** {signal['direction']}")
    st.write(f"**Entry Point:** ${signal['entry_point']}")
    st.write(f"**Confidence:** {signal['confidence']}%")
    st.write(f"**Momentum:** {signal['momentum']}")
    st.write(f"**Prediction:** {signal['prediction']}")
    st.write(f"**Profitability:** {signal['profitability']}")
    st.write(f"**Up Probability:** {signal['up_probability']}%")
    st.write(f"**Down Probability:** {signal['down_probability']}%")
    st.write(signal['only_max'])

if __name__ == "__main__":
    try:
        import streamlit.web.bootstrap  # Just to detect streamlit environment
        import sys
        if any("streamlit" in arg for arg in sys.argv):
            streamlit_main()
        else:
            cli_main()
    except:
        cli_main()
