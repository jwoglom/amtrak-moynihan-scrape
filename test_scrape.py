#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock
from scrape import parse, Train, scrape, ScheduleBoard

class TestParse(unittest.TestCase):
    def test_parse_golden_input_departures(self):
        # Golden input
        golden_html = """<table id="amtrak-departures" class="amtrak-table departures"><thead class="placeholder-head"><tr><th></th><th></th><th></th></tr></thead><tbody><tr class="amtrak-header-row"><td>6:45 PM</td><td colspan="2"><span class="train-number">241</span>&nbsp;<span class="train-name">Empire Service</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Albany-Rensselaer, NY</span><span class="pill-status ">Second Boarding</span></td><td class="track-cell">6</td></tr><tr class="amtrak-header-row"><td>7:01 PM</td><td colspan="2"><span class="train-number">57</span>&nbsp;<span class="train-name">Vermonter</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Washington, DC</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:15 PM</td><td colspan="2"><span class="train-number">2258</span>&nbsp;<span class="train-name">Acela</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Boston, MA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:30 PM</td><td colspan="2"><span class="train-number">132</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Boston, MA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:53 PM</td><td colspan="2"><span class="train-number">671</span>&nbsp;<span class="train-name">Keystone Service</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Harrisburg, PA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:59 PM</td><td colspan="2"><span class="train-number">165</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Washington, DC</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>8:00 PM</td><td colspan="2"><span class="train-number">146</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">New Haven, CT</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>8:29 PM</td><td colspan="2"><span class="train-number">2259</span>&nbsp;<span class="train-name">Acela</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Washington, DC</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>9:00 PM</td><td colspan="2"><span class="train-number">166</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Boston, MA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>9:20 PM</td><td colspan="2"><span class="train-number">2275</span>&nbsp;<span class="train-name">Acela</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Washington, DC</span><span class="pill-status ">Now 9:25PM</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>9:22 PM</td><td colspan="2"><span class="train-number">139</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Philadelphia, PA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr></tbody></table>"""
        
        # Parse the HTML
        trains = parse(golden_html)
        
        # Verify we got the expected number of trains
        self.assertEqual(len(trains), 11)
        
        # Test first train
        first_train = trains[0]
        self.assertEqual(first_train.time, "6:45 PM")
        self.assertEqual(first_train.train_number, "241")
        self.assertEqual(first_train.train_name, "Empire Service")
        self.assertEqual(first_train.destination, "Albany-Rensselaer, NY")
        self.assertEqual(first_train.status, "Second Boarding")
        self.assertEqual(first_train.track, "6")
        
        # Test second train
        second_train = trains[1]
        self.assertEqual(second_train.time, "7:01 PM")
        self.assertEqual(second_train.train_number, "57")
        self.assertEqual(second_train.train_name, "Vermonter")
        self.assertEqual(second_train.destination, "Washington, DC")
        self.assertEqual(second_train.status, "On Time")
        self.assertEqual(second_train.track, "")
        
        # Test a train with different characteristics (Acela)
        acela_train = trains[2]  # 7:15 PM Acela
        self.assertEqual(acela_train.time, "7:15 PM")
        self.assertEqual(acela_train.train_number, "2258")
        self.assertEqual(acela_train.train_name, "Acela")
        self.assertEqual(acela_train.destination, "Boston, MA")
        self.assertEqual(acela_train.status, "On Time")
        self.assertEqual(acela_train.track, "")
        
        # Test a train with delayed status
        delayed_train = trains[9]  # 9:20 PM Acela with delay
        self.assertEqual(delayed_train.time, "9:20 PM")
        self.assertEqual(delayed_train.train_number, "2275")
        self.assertEqual(delayed_train.train_name, "Acela")
        self.assertEqual(delayed_train.destination, "Washington, DC")
        self.assertEqual(delayed_train.status, "Now 9:25PM")
        self.assertEqual(delayed_train.track, "")
        
        # Test last train
        last_train = trains[-1]
        self.assertEqual(last_train.time, "9:22 PM")
        self.assertEqual(last_train.train_number, "139")
        self.assertEqual(last_train.train_name, "Northeast Regional")
        self.assertEqual(last_train.destination, "Philadelphia, PA")
        self.assertEqual(last_train.status, "On Time")
        self.assertEqual(last_train.track, "")
        
        # Verify all trains have the expected structure
        for train in trains:
            self.assertIsInstance(train, Train)
            self.assertIsInstance(train.time, str)
            self.assertIsInstance(train.train_number, str)
            self.assertIsInstance(train.train_name, str)
            self.assertIsInstance(train.destination, str)
            self.assertIsInstance(train.status, str)
            self.assertIsInstance(train.track, str)
            self.assertGreater(len(train.time), 0)
            self.assertGreater(len(train.train_number), 0)
            self.assertGreater(len(train.train_name), 0)
            self.assertGreater(len(train.destination), 0)
            self.assertGreater(len(train.status), 0)

    def test_parse_empty_input(self):
        """Test parsing empty HTML input"""
        trains = parse("")
        self.assertEqual(trains, [])
    
    def test_parse_no_trains(self):
        """Test parsing HTML with no train data"""
        html_without_trains = "<html><body><table><tbody></tbody></table></body></html>"
        trains = parse(html_without_trains)
        self.assertEqual(trains, [])

    def test_parse_golden_input_arrivals(self):
        # Golden input for arrivals
        golden_html = """<table id="amtrak-arrivals" class="amtrak-table arrivals"><tbody><tr class="amtrak-header-row"><td>7:02 PM</td><td colspan="2"><span class="train-number">67</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Boston, MA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:24 PM</td><td colspan="2"><span class="train-number">90</span>&nbsp;<span class="train-name">Palmetto</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Savannah, GA</span><span class="pill-status ">Now 11:15PM</span></td><td class="track-cell"></td></tr><tr class="amtrak-header-row"><td>7:59 PM</td><td colspan="2"><span class="train-number">169</span>&nbsp;<span class="train-name">Northeast Regional</span></td></tr><tr class="amtrak-destination"><td colspan="2" class="pill-cell"><span class="pill-destination">Boston, MA</span><span class="pill-status ">On Time</span></td><td class="track-cell"></td></tr></tbody></table>"""
        
        # Parse the HTML
        trains = parse(golden_html)
        
        # Verify we got the expected number of trains
        self.assertEqual(len(trains), 3)
        
        # Test first train
        first_train = trains[0]
        self.assertEqual(first_train.time, "7:02 PM")
        self.assertEqual(first_train.train_number, "67")
        self.assertEqual(first_train.train_name, "Northeast Regional")
        self.assertEqual(first_train.destination, "Boston, MA")
        self.assertEqual(first_train.status, "On Time")
        self.assertEqual(first_train.track, "")
        
        # Test a train with delayed status
        delayed_train = trains[1]  # 7:24 PM Palmetto
        self.assertEqual(delayed_train.time, "7:24 PM")
        self.assertEqual(delayed_train.train_number, "90")
        self.assertEqual(delayed_train.train_name, "Palmetto")
        self.assertEqual(delayed_train.destination, "Savannah, GA")
        self.assertEqual(delayed_train.status, "Now 11:15PM")
        self.assertEqual(delayed_train.track, "")
        
        # Test last train
        last_train = trains[-1]
        self.assertEqual(last_train.time, "7:59 PM")
        self.assertEqual(last_train.train_number, "169")
        self.assertEqual(last_train.train_name, "Northeast Regional")
        self.assertEqual(last_train.destination, "Boston, MA")
        self.assertEqual(last_train.status, "On Time")
        self.assertEqual(last_train.track, "")
        
        # Verify all trains have the expected structure
        for train in trains:
            self.assertIsInstance(train, Train)
            self.assertIsInstance(train.time, str)
            self.assertIsInstance(train.train_number, str)
            self.assertIsInstance(train.train_name, str)
            self.assertIsInstance(train.destination, str)
            self.assertIsInstance(train.status, str)
            self.assertIsInstance(train.track, str)
            self.assertGreater(len(train.time), 0)
            self.assertGreater(len(train.train_number), 0)
            self.assertGreater(len(train.train_name), 0)
            self.assertGreater(len(train.destination), 0)
            self.assertGreater(len(train.status), 0)


class TestScrape(unittest.TestCase):
    @patch('scrape.primp.get')
    def test_scrape_success(self, mock_get):
        """Test the scrape() function with mocked HTTP response"""
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <table id="amtrak-departures-target">
                    <tbody>
                        <tr class="amtrak-header-row">
                            <td>6:45 PM</td>
                            <td colspan="2">
                                <span class="train-number">241</span>&nbsp;
                                <span class="train-name">Empire Service</span>
                            </td>
                        </tr>
                        <tr class="amtrak-destination">
                            <td colspan="2" class="pill-cell">
                                <span class="pill-destination">Albany-Rensselaer, NY</span>
                                <span class="pill-status ">Second Boarding</span>
                            </td>
                            <td class="track-cell">6</td>
                        </tr>
                        <tr class="amtrak-header-row">
                            <td>7:01 PM</td>
                            <td colspan="2">
                                <span class="train-number">57</span>&nbsp;
                                <span class="train-name">Vermonter</span>
                            </td>
                        </tr>
                        <tr class="amtrak-destination">
                            <td colspan="2" class="pill-cell">
                                <span class="pill-destination">Washington, DC</span>
                                <span class="pill-status ">On Time</span>
                            </td>
                            <td class="track-cell"></td>
                        </tr>
                    </tbody>
                </table>
                <table id="amtrak-arrivals-target">
                    <tbody>
                        <tr class="amtrak-header-row">
                            <td>7:02 PM</td>
                            <td colspan="2">
                                <span class="train-number">67</span>&nbsp;
                                <span class="train-name">Northeast Regional</span>
                            </td>
                        </tr>
                        <tr class="amtrak-destination">
                            <td colspan="2" class="pill-cell">
                                <span class="pill-destination">Boston, MA</span>
                                <span class="pill-status ">On Time</span>
                            </td>
                            <td class="track-cell"></td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Call the scrape function
        result = scrape()
        
        # Verify the function was called with correct parameters
        mock_get.assert_called_once_with(
            'https://moynihantrainhall.nyc/transportation/',
            headers={'Referer': 'https://moynihantrainhall.nyc/'}
        )
        
        # Verify the result structure
        self.assertIsInstance(result, ScheduleBoard)
        self.assertIsInstance(result.departures, list)
        self.assertIsInstance(result.arrivals, list)
        
        # Verify departures
        self.assertEqual(len(result.departures), 2)
        self.assertEqual(result.departures[0].time, "6:45 PM")
        self.assertEqual(result.departures[0].train_number, "241")
        self.assertEqual(result.departures[0].train_name, "Empire Service")
        self.assertEqual(result.departures[0].destination, "Albany-Rensselaer, NY")
        self.assertEqual(result.departures[0].status, "Second Boarding")
        self.assertEqual(result.departures[0].track, "6")
        
        self.assertEqual(result.departures[1].time, "7:01 PM")
        self.assertEqual(result.departures[1].train_number, "57")
        self.assertEqual(result.departures[1].train_name, "Vermonter")
        self.assertEqual(result.departures[1].destination, "Washington, DC")
        self.assertEqual(result.departures[1].status, "On Time")
        self.assertEqual(result.departures[1].track, "")
        
        # Verify arrivals
        self.assertEqual(len(result.arrivals), 1)
        self.assertEqual(result.arrivals[0].time, "7:02 PM")
        self.assertEqual(result.arrivals[0].train_number, "67")
        self.assertEqual(result.arrivals[0].train_name, "Northeast Regional")
        self.assertEqual(result.arrivals[0].destination, "Boston, MA")
        self.assertEqual(result.arrivals[0].status, "On Time")
        self.assertEqual(result.arrivals[0].track, "")

    @patch('scrape.primp.get')
    def test_scrape_http_error(self, mock_get):
        """Test the scrape() function handles HTTP errors properly"""
        # Mock response with error status code
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # Verify that the function raises an exception
        with self.assertRaises(Exception) as context:
            scrape()
        
        # Verify the exception message
        self.assertIn("Failed to scrape: 404", str(context.exception))
        self.assertIn("Not Found", str(context.exception))

if __name__ == '__main__':
    unittest.main()
