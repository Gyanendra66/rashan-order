# Store notes

These sites change their layout often, so nothing here names buttons or selectors. Look at the page as it is now and find the element by what it does. If the page contradicts these notes, trust the page.

## Common to all stores

- Stock, price and delivery fee depend on the delivery location. Confirm the address shown at the top of the site before searching, otherwise the cart can empty itself when the address is corrected at checkout.
- Search by the plain product name first ("toor dal"), then narrow by brand and size from the results. Searching the full string with brand and size often returns nothing.
- Compare pack size *and* count: "500 g x 2" and "1 kg" are different listings with different prices. Match the list's quantity by total amount.
- Fees appear late: delivery, handling, small-cart, surge or rain fees are usually only final on the cart/checkout page. Take the summary numbers from that page, not from adding up product prices.
- Minimum order values exist. If the cart is below it, tell the user the shortfall and let them decide; do not pad the cart.
- Tip, donation and "add for free delivery" prompts are often pre-selected or one tap away. Make sure none is included.
- Order confirmation gives an order ID and ETA. If the page does not show one, look in "My orders".

## Blinkit (default)

- Web: blinkit.com. Login is by mobile number + OTP; the user does this themselves.
- Quick-commerce: delivery in minutes, so the user should be home when a scheduled order is approved. Mention the ETA in the summary.
- UPI at checkout: usually either "pay via UPI app" (shows a QR / opens an intent, awkward on desktop) or "enter UPI ID" (sends a collect request to the user's UPI app). On desktop prefer the UPI ID route using the configured `upi_id`; if only a QR is shown, tell the user to scan it from their phone.
- Payment requests expire in a few minutes. Tell the user the request is waiting as soon as it is sent.

## Zepto, Swiggy Instamart, BigBasket

Same flow. Differences worth knowing:
- Some of these push the mobile app and limit the website; if checkout is not possible on the web, tell the user and hand over the due list.
- BigBasket uses delivery slots rather than instant delivery: include the chosen slot in the final summary, since picking a slot is a decision the user should see.

## A local shop

If the user's kirana takes orders by website, use the same flow. If it takes orders by WhatsApp or phone, do not message or call anyone on the user's behalf unprompted: draft the order message (items, quantities, address label) and give it to the user to send. Payment then happens between the user and the shop.
