import metricbeat
import os
import pytest
import sys
import unittest


@metricbeat.parameterized_with_supported_versions
class Test(metricbeat.BaseTest):

    COMPOSE_SERVICES = ['postgresql']

    def common_checks(self, output):
        # Ensure no errors or warnings exist in the log.
        self.assert_no_logged_warnings()

        for evt in output:
            top_level_fields = metricbeat.COMMON_FIELDS + ["postgresql"]
            self.assertCountEqual(self.de_dot(top_level_fields), evt.keys())

            self.assert_fields_are_documented(evt)

    def get_hosts(self):
        username = "postgres"
        password = os.getenv("POSTGRESQL_PASSWORD", default="postgres")
        host = self.compose_host()
        dsn = "postgres://{}?sslmode=disable".format(host)
        return ([dsn], username, password)

    @unittest.skipUnless(metricbeat.INTEGRATION_TESTS, "integration test")
    @pytest.mark.tag('integration')
    def test_activity(self):
        """
        PostgreSQL module outputs an event.
        """
        hosts, username, password = self.get_hosts()
        self.render_config_template(modules=[{
            "name": "postgresql",
            "metricsets": ["activity"],
            "hosts": hosts,
            "username": username,
            "password": password,
            "period": "5s"
        }])
        proc = self.start_beat()
        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()

        output = self.read_output_json()
        self.common_checks(output)

        for evt in output:
            if "database" in evt["postgresql"]["activity"]:
                assert "name" in evt["postgresql"]["activity"]["database"]
                assert "oid" in evt["postgresql"]["activity"]["database"]
                assert "state" in evt["postgresql"]["activity"]
            else:
                assert "backend_type" in evt["postgresql"]["activity"]

    @unittest.skipUnless(metricbeat.INTEGRATION_TESTS, "integration test")
    @pytest.mark.tag('integration')
    def test_database(self):
        """
        PostgreSQL module outputs an event.
        """
        hosts, username, password = self.get_hosts()
        self.render_config_template(modules=[{
            "name": "postgresql",
            "metricsets": ["database"],
            "hosts": hosts,
            "username": username,
            "password": password,
            "period": "5s"
        }])
        proc = self.start_beat()
        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()

        output = self.read_output_json()
        self.common_checks(output)

        for evt in output:
            assert "name" in evt["postgresql"]["database"]
            assert "oid" in evt["postgresql"]["database"]
            assert "blocks" in evt["postgresql"]["database"]
            assert "rows" in evt["postgresql"]["database"]
            assert "conflicts" in evt["postgresql"]["database"]
            assert "deadlocks" in evt["postgresql"]["database"]

    @unittest.skipUnless(metricbeat.INTEGRATION_TESTS, "integration test")
    @pytest.mark.tag('integration')
    def test_bgwriter(self):
        """
        PostgreSQL module outputs an event.
        """
        hosts, username, password = self.get_hosts()
        self.render_config_template(modules=[{
            "name": "postgresql",
            "metricsets": ["bgwriter"],
            "hosts": hosts,
            "username": username,
            "password": password,
            "period": "5s"
        }])
        proc = self.start_beat()
        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()

        output = self.read_output_json()
        self.common_checks(output)

        for evt in output:
            assert "checkpoints" in evt["postgresql"]["bgwriter"]
            assert "buffers" in evt["postgresql"]["bgwriter"]
            assert "stats_reset" in evt["postgresql"]["bgwriter"]

    @unittest.skipUnless(metricbeat.INTEGRATION_TESTS, "integration test")
    @pytest.mark.tag('integration')
    def test_statement(self):
        """
        PostgreSQL module outputs an event.
        """
        hosts, username, password = self.get_hosts()
        self.render_config_template(modules=[{
            "name": "postgresql",
            "metricsets": ["statement"],
            "hosts": hosts,
            "username": username,
            "password": password,
            "period": "5s"
        }])
        proc = self.start_beat()
        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()

        output = self.read_output_json()
        self.common_checks(output)

        for evt in output:
            statement = evt["postgresql"]["statement"]
            assert "user" in statement
            assert "database" in statement
            assert "query" in statement
            assert "ms" in statement["query"]["time"]["max"]
            assert "ms" in statement["query"]["time"]["total"]
