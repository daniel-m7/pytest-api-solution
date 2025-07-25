from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
2) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
3) Validate the response codes and values
4) Validate the response message "Order and pet status updated successfully"
'''
#Notes
# - Need to ensure that theres always a pet available
# - can do this with a reset fixture

@pytest.fixture
def create_test_order():
    for pet_id in [0, 1, 2]:
        pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
        if pet_response.status_code == 200:
            pet_data = pet_response.json()
            if pet_data['status'] == 'available':
                order_data = {"pet_id": pet_id}
                response = api_helpers.post_api_data("/store/order", order_data)
                if response.status_code == 201:
                    return response.json()
    pytest.skip("No available pets")


@pytest.mark.parametrize("new_status", ["sold", "pending", "available"])
def test_patch_order_by_id(create_test_order, new_status):
    order = create_test_order
    order_id = order['id']
    
    update_data = {"status": new_status}
    
    # Send patch request
    response = api_helpers.patch_api_data(f"/store/order/{order_id}", update_data)
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert_that(response_data['message'], is_("Order and pet status updated successfully"))
    
    # Validate updated pet status
    pet_response = api_helpers.get_api_data(f"/pets/{order['pet_id']}")
    assert pet_response.status_code == 200
    pet_data = pet_response.json()
    assert_that(pet_data['status'], is_(new_status))

def test_create_order():
    # Test post request to create an order

    for pet_id in [0, 1, 2]:
        pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
        if pet_response.status_code == 200:
            pet_data = pet_response.json()
            if pet_data['status'] == 'available':

                # Create the order
                order_data = {"pet_id": pet_id}
                response = api_helpers.post_api_data("/store/order", order_data)
                
                assert response.status_code == 201
                
                # Validate order schema
                order = response.json()
                validate(instance=order, schema=schemas.order)
                
                # Make sure order contains expected data
                assert_that(order['pet_id'], is_(pet_id))
                assert_that(order['status'], is_("pending"))  # New orders start as pending
                
                return
    
    pytest.skip("No available pets for order creation test")