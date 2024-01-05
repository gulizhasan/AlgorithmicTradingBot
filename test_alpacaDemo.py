import pytest
from unittest.mock import Mock, patch
import alpacaDemo

# Test for the analyze_market_data function
def test_analyze_market_data():
    # Mocking the external API calls and any other external dependencies
    with patch('alpacaDemo.is_market_open', return_value=True), \
         patch('alpacaDemo.place_order') as mock_place_order:
        
        # Sample data to be used for testing
        test_data = {'t': 1654123200000, 'c': 150}  # Example data
        symbol = 'AAPL'

        # Call the function with test data
        alpacaDemo.analyze_market_data(symbol, test_data)

        # Assertions to verify expected behavior
        mock_place_order.assert_called()
