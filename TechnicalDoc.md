
## Auth API

```
curl --location 'https://apiv2.shiprocket.in/v1/auth/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "${EMAIL}",
    "password":"${PASSWORD}"
}'
```

## Order Creation API

```curl --location 'https://apiv2.shiprocket.in/v1/orders/create/adhoc' \
--header 'accept: application/json' \
--header 'accept-language: en-GB,en-US;q=0.9,en;q=0.8' \
--header 'authorization: Bearer ${AUTH_TOKEN}' \
--header 'content-type: application/json' \
--header 'cookie: intercom-device-id-vg83whu4=d997ec1a-93dc-4bd8-a1bd-74e40918d186; _cs_c=1; _clck=1gpc5wb%7C2%7Cfm6%7C0%7C1596; UTM=%7B%22referrer%22%3A%22https%3A%2F%2Fapp.shiprocket.in%2Fseller%2Forders%2Fnew%3Fsku%3D%26order_ids%3D%26order_status%3D%26channel_id%3D%26payment_method%3D%26pickup_address_id%3D%26rto_status%3D%26delivery_country%3D%26quantity%3D%26tags%3D%26from%3D2024-Jun-18%26to%3D2024-Jul-17%22%2C%22pathname%22%3A%22%2Flogin%22%7D; intercom-session-vg83whu4=OWJTbTBVMC9XMEk3UWQ3eXBab3Nwc1ZmV1NXSVJ3a1prejBpR2hCd0pSaVBJT2ozYkJQVXc3NnREWGZXZC80Zi0tRXdrQk96Uk9ubDJxTnpGRnR6MmsvQT09--f49bf2faaeba01d182b6faaa91a1c57c7d9bfaf5' \
--header 'cookiie: _ufp=aStITlpPVUhweFM0c3dHK1FKbTdzc0pya2RKd05JWUlBSHpFeExHU05Ea3JxU3pVbUt3RngwKy9md2paUlhhaGtlRk9BYUlnVVJKVzA0TjJJeEJXRmc9PQ==; catalogueBanner=true; keyboardShortcutPopup=true; whatsappCommPopup=true; company_insurance_popup=Thu%20Jul%2025%202024%2012%3A32%3A05%20GMT%2B0530%20(India%20Standard%20Time); cus_device=97b8ac27028fd97e46b230da8e4e2274; cus_device2=97b8ac27028fd97e46b230da8e4e22741709025232052; intercom-device-id-vg83whu4=d997ec1a-93dc-4bd8-a1bd-74e40918d186; _cs_c=1; _clck=1gpc5wb%7C2%7Cfm6%7C0%7C1596; NPS_397ff8f2_last_seen=1718807127972; user_device_id=%5B%2297b8ac27028fd97e46b230da8e4e2274%22%5D; UTM=%7B%22referrer%22%3A%22https%3A%2F%2Fapp.shiprocket.in%2Fseller%2Forders%2Fnew%3Fsku%3D%26order_ids%3D%26order_status%3D%26channel_id%3D%26payment_method%3D%26pickup_address_id%3D%26rto_status%3D%26delivery_country%3D%26quantity%3D%26tags%3D%26from%3D2024-Jun-18%26to%3D2024-Jul-17%22%2C%22pathname%22%3A%22%2Flogin%22%7D; first_utm=%7B%22referrer%22%3A%22https%3A%2F%2Fapp.shiprocket.in%2Fseller%2Forders%2Fnew%3Fsku%3D%26order_ids%3D%26order_status%3D%26channel_id%3D%26payment_method%3D%26pickup_address_id%3D%26rto_status%3D%26delivery_country%3D%26quantity%3D%26tags%3D%26from%3D2024-Jun-18%26to%3D2024-Jul-17%22%2C%22pathname%22%3A%22%2Flogin%22%7D; intercom-session-vg83whu4=OWJTbTBVMC9XMEk3UWQ3eXBab3Nwc1ZmV1NXSVJ3a1prejBpR2hCd0pSaVBJT2ozYkJQVXc3NnREWGZXZC80Zi0tRXdrQk96Uk9ubDJxTnpGRnR6MmsvQT09--f49bf2faaeba01d182b6faaa91a1c57c7d9bfaf5' \
--header 'dnt: 1' \
--header 'no-auth: True' \
--header 'origin: https://app.shiprocket.in' \
--header 'priority: u=1, i' \
--header 'referer: https://app.shiprocket.in/' \
--header 'sec-ch-ua: "Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"' \
--header 'sec-ch-ua-mobile: ?0' \
--header 'sec-ch-ua-platform: "Linux"' \
--header 'sec-fetch-dest: empty' \
--header 'sec-fetch-mode: cors' \
--header 'sec-fetch-site: same-site' \
--header 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
--data-raw '{
    "order_id": "75854226637PC12011",
    "isd_code": "+91",
    "billing_isd_code": "+91",
    "order_date": "2025-06-02",
    "channel_id": "",
    "billing_customer_name": "test ",
    "billing_last_name": "",
    "billing_address": "road 1, shop2,test 123",
    "billing_address_2": "",
    "billing_city": "K.V.Rangareddy",
    "billing_state": "3976",
    "billing_country": "India",
    "billing_pincode": "110030",
    "billing_email": "test@g.com",
    "billing_phone": "9999999912",
    "landmark": "",
    "latitude": "",
    "longitude": "",
    "shipping_is_billing": 0,
    "shipping_customer_name": "Pooja c",
    "shipping_last_name": "",
    "shipping_address": "abc11, road number-123/456,just testing",
    "shipping_address_2": "near xyz road",
    "shipping_city": "South Delhi",
    "order_type": "",
    "shipping_country": "India",
    "shipping_pincode": "110030",
    "shipping_state": "Delhi",
    "shipping_email": "p@g.com",
    "product_category": "",
    "shipping_phone": "9999999912",
    "billing_alternate_phone": "",
    "order_items": [
        {
            "name": "High_weight",
            "selling_price": "111",
            "units": 1,
            "category_name": null,
            "hsn": "",
            "sku": "high_weight",
            "tax": null,
            "discount": null,
            "product_description": null,
            "optionalValueStatus": null,
            "caetgroy_code": "",
            "category_id": "",
            "weight": 1
        }
    ],
    "payment_method": "prepaid",
    "shipping_charges": "",
    "giftwrap_charges": "11",
    "transaction_charges": "11",
    "total_discount": "11",
    "sub_total": 6000,
    "weight": 1,
    "length": 10,
    "breadth": 11,
    "height": 11,
    "pickup_location": "Pickup-Monika",
    "reseller_name": "",
    "company_name": "",
    "ewaybill_no": "",
    "customer_gstin": "",
    "is_order_revamp": 1,
    "is_document": 0,
    "order_tag": "",
    "delivery_challan": "false",
    "is_web": 1,
    "is_send_notification": true,
    "is_insurance_opt": 0,
    "purpose_of_shipment": "",
    "currency": "INR"
}
```

