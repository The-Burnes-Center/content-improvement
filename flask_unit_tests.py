import unittest
from unittest.mock import patch, MagicMock
from flask_backend import app

class AddProjectRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.payload = {
            "userId": 1,
            "url": "http://example.com",
            "name": "My Project"
        }

    @patch('flask_backend.mysql.connect')
    def test_add_project_success(self, mock_mysql_connect):
        # Setup mock DB connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.post('/add_project', json=self.payload)

        # ✅ Assert correct HTTP response
        self.assertEqual(response.status_code, 201)
        self.assertIn(b"Project added successfully", response.data)

        # ✅ Assert DB methods were called correctly
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO Project (userId, url, name) VALUES (%s, %s, %s)",
            (1, "http://example.com", "My Project")
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('flask_backend.mysql.connect')
    def test_add_project_missing_fields(self, mock_mysql_connect):
        # Remove 'url' to simulate bad input
        bad_payload = {
            "userId": 1,
            "name": "Incomplete Project"
        }

        response = self.client.post('/add_project', json=bad_payload)

        # You might want to add validation in the real route to handle this better
        self.assertEqual(response.status_code, 500)  # Likely a server error due to bad SQL args
