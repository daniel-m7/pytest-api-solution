from jsonschema import validate
import pytest
import schemas
import api_helpers
import uuid
from hamcrest import assert_that, contains_string, is_

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
2) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
3) Validate the response codes and values
4) Validate the response message "Order and pet status updated successfully"
'''

# I decided to generate unique pet ids instead of using the in memory store
# This is so that I am able to test the full API workflow, also enhances test isolation

# The factory pattern has the benefit of creating new data for each parameterized test run

@pytest.fixture
def create_test_order():

    # Track pets created during this test for cleanup
    created_pets = []  
    
    def _create_order():

        # Generate unique pet ID to avoid conflicts with test_pet.py 404 tests, using 1000000+ to avoid collisions 
        unique_pet_id = 1000000 + (int(f"9{uuid.uuid4().hex[:7]}", 16) % 8999999)
        
        # Create a new pet thats available
        pet_data = {
            "id": unique_pet_id,
            "name": f"test_pet_{uuid.uuid4().hex[:8]}",
            "type": "dog", 
            "status": "available"
        }
        
        # Create the new pet
        pet_response = api_helpers.post_api_data("/pets", pet_data)
        if pet_response.status_code != 201:
            pytest.fail(f"Failed to create test pet: {pet_response.text}")
        
        # Track this pet for cleanup
        created_pets.append(unique_pet_id)
        
        # Create order with the new pet
        order_data = {"pet_id": unique_pet_id, "status": "pending"}
        order_response = api_helpers.post_api_data("/store/order", order_data)
        
        # Validate order creation
        if order_response.status_code != 201:
            pytest.fail(f"Failed to create test order: {order_response.text}")
            
        return order_response.json()
    
    # Return the function for fresh execution each time
    yield _create_order
    
    # Cleanup created pets
    for pet_id in created_pets:
        try:
            api_helpers.delete_api_data(f"/pets/{pet_id}")
        except Exception:
            pass


# Testing the PATCH endpoint with all statuses

# I call create_test_order to get new data for each test run so that tests dont interfere with each other

# Im checking:
# The API responds with 200 with the right messsage
# When order status is updated, so is the pet status

@pytest.mark.parametrize("new_status", ["sold", "pending", "available"])
def test_patch_order_by_id(create_test_order, new_status):


    order = create_test_order() 
    order_id = order['id']
    pet_id = order['pet_id']
    
    # Prepare update payload
    update_data = {"status": new_status}
    
    # PATCH request with error context
    response = api_helpers.patch_api_data(f"/store/order/{order_id}", update_data)
    
    # Validate PATCH response with error message
    assert response.status_code == 200, f"PATCH failed for status '{new_status}': {response.text}"
    
    # Validate response message
    response_data = response.json()
    assert_that(response_data['message'], is_("Order and pet status updated successfully"))
    
    # Pet status should match order status
    pet_response = api_helpers.get_api_data(f"/pets/{pet_id}")
    assert pet_response.status_code == 200, f"Failed to fetch pet {pet_id} after order update"
    
    #
    pet_data = pet_response.json()
    assert_that(pet_data['status'], is_(new_status), 
                f"Pet {pet_id} status should be '{new_status}' after order update")



def test_create_order(create_test_order):
    # Test post request to create an order using unique pet
    order = create_test_order()  
    
    # The status might not be returned, so see what comes back
    assert 'id' in order, "Order should have an ID"
    assert 'pet_id' in order, "Order should have a pet_id"
    assert_that(order['pet_id'], is_(int))
    
    # Vaildate status if in response
    if 'status' in order:
        assert_that(order['status'], is_("pending"))
        # Only validate schema if all required fields are present
        validate(instance=order, schema=schemas.order)
