#!/usr/bin/env python3
"""
Unit tests for report generator.
"""

import json
import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from generate_report import TemplateRenderer, ReportGenerator


class TestTemplateRenderer:
    """Test suite for TemplateRenderer class."""

    def test_process_simple_variables(self):
        """Test rendering simple variables."""
        template = "Hello {{name}}, you have {{count}} messages."
        renderer = TemplateRenderer(template)
        result = renderer.render({'name': 'Alice', 'count': 5})

        assert result == "Hello Alice, you have 5 messages."

    def test_process_missing_variables(self):
        """Test that missing variables are left unchanged."""
        template = "Hello {{name}}, {{missing}} variable."
        renderer = TemplateRenderer(template)
        result = renderer.render({'name': 'Bob'})

        assert "Bob" in result
        assert "{{missing}}" in result

    def test_process_each_block(self):
        """Test rendering #each blocks."""
        template = """Items:
{{#each items}}
- {{this.name}}: {{this.value}}
{{/each}}"""
        renderer = TemplateRenderer(template)
        data = {
            'items': [
                {'name': 'Item1', 'value': 10},
                {'name': 'Item2', 'value': 20}
            ]
        }
        result = renderer.render(data)

        assert "Item1: 10" in result
        assert "Item2: 20" in result

    def test_process_each_empty_list(self):
        """Test rendering #each with empty list."""
        template = "{{#each items}}Item{{/each}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({'items': []})

        assert result == ""

    def test_process_each_missing_key(self):
        """Test rendering #each with missing key."""
        template = "{{#each items}}Item{{/each}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({})

        assert result == ""

    def test_process_if_block_true(self):
        """Test rendering #if block when condition is true."""
        template = "{{#if has_data}}Data available{{/if}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({'has_data': True})

        assert result == "Data available"

    def test_process_if_block_false(self):
        """Test rendering #if block when condition is false."""
        template = "{{#if has_data}}Data available{{/if}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({'has_data': False})

        assert result == ""

    def test_process_if_else_block_true(self):
        """Test rendering #if...else block when condition is true."""
        template = "{{#if has_data}}Yes{{else}}No{{/if}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({'has_data': True})

        assert result == "Yes"

    def test_process_if_else_block_false(self):
        """Test rendering #if...else block when condition is false."""
        template = "{{#if has_data}}Yes{{else}}No{{/if}}"
        renderer = TemplateRenderer(template)
        result = renderer.render({'has_data': False})

        assert result == "No"

    def test_process_nested_properties(self):
        """Test rendering nested properties in #each blocks."""
        template = """{{#each items}}
Score: {{this.factors.severity}}
{{/each}}"""
        renderer = TemplateRenderer(template)
        data = {
            'items': [
                {'factors': {'severity': 100}},
                {'factors': {'severity': 75}}
            ]
        }
        result = renderer.render(data)

        assert "100" in result
        assert "75" in result

    def test_complex_template(self):
        """Test rendering a complex template with multiple features."""
        template = """# Report for {{name}}

Total: {{total}}

{{#if has_items}}
Items:
{{#each items}}
- {{this.title}} ({{this.priority}})
{{/each}}
{{else}}
No items found
{{/if}}"""

        renderer = TemplateRenderer(template)
        data = {
            'name': 'Test Project',
            'total': 2,
            'has_items': True,
            'items': [
                {'title': 'Bug fix', 'priority': 'P0'},
                {'title': 'Feature', 'priority': 'P1'}
            ]
        }
        result = renderer.render(data)

        assert "Test Project" in result
        assert "Total: 2" in result
        assert "Bug fix" in result
        assert "P0" in result
        assert "No items found" not in result


class TestReportGenerator:
    """Test suite for ReportGenerator class."""

    @pytest.fixture
    def temp_template(self):
        """Create a temporary template file."""
        template_content = """# Priority Report

Generated: {{timestamp}}
Total Items: {{total_items}}

{{#each top_items}}
## {{this.id}}: {{this.title}}
- Score: {{this.priority_score}}
- Rationale: {{this.rationale}}
{{/each}}

Recommendations:
{{#each recommendations}}
- {{this}}
{{/each}}"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(template_content)
            return Path(f.name)

    @pytest.fixture
    def sample_data(self):
        """Create sample report data."""
        return {
            'analysis_type': 'Test Analysis',
            'items': [
                {
                    'id': 'BUG-001',
                    'title': 'Critical Bug',
                    'priority_score': 95.5,
                    'priority_factors': {
                        'severity': 100,
                        'dependencies': 75,
                        'impact': 100,
                        'effort': 75,
                        'age': 80,
                        'frequency': 50
                    },
                    'blocked': False
                },
                {
                    'id': 'FEAT-001',
                    'title': 'New Feature',
                    'priority_score': 65.0,
                    'priority_factors': {
                        'severity': 10,
                        'dependencies': 0,
                        'impact': 50,
                        'effort': 100,
                        'age': 40,
                        'frequency': 25
                    },
                    'blocked': False
                }
            ],
            'dependencies': {
                'critical_path': ['BUG-003', 'BUG-001', 'FEAT-002'],
                'circular_dependencies': []
            },
            'patterns': {
                'velocity_trend': [
                    {'week': '2025-W40', 'items_completed': 5, 'points_completed': 15},
                    {'week': '2025-W41', 'items_completed': 6, 'points_completed': 18},
                    {'week': '2025-W42', 'items_completed': 7, 'points_completed': 21}
                ],
                'completion_time_by_component': {
                    'core': {'mean': 8, 'median': 6, 'stdev': 2},
                    'ui': {'mean': 3, 'median': 2, 'stdev': 1}
                },
                'effort_accuracy': {
                    'mean_error': 25,
                    'median_error': 20,
                    'typically_underestimate': True,
                    'adjustment_factor': 1.25
                }
            },
            'recommendations': [
                'Focus on critical bugs first',
                'Consider parallelizing UI work'
            ]
        }

    def test_initialization(self, temp_template):
        """Test that generator initializes correctly."""
        generator = ReportGenerator(temp_template)
        assert generator.template_path == temp_template
        assert generator.template_content is not None
        assert generator.renderer is not None
        temp_template.unlink()  # Cleanup

    def test_generate_rationale_critical_severity(self):
        """Test generating rationale for critical severity."""
        generator = ReportGenerator(Path(__file__))  # Dummy path
        item = {
            'priority_factors': {
                'severity': 100,
                'dependencies': 0,
                'impact': 50,
                'effort': 50,
                'age': 50,
                'frequency': 25
            }
        }
        rationale = generator._generate_rationale(item)

        assert "critical severity" in rationale

    def test_generate_rationale_blocks_items(self):
        """Test generating rationale for blocking dependencies."""
        generator = ReportGenerator(Path(__file__))
        item = {
            'priority_factors': {
                'severity': 50,
                'dependencies': 100,
                'impact': 50,
                'effort': 50,
                'age': 50,
                'frequency': 25
            }
        }
        rationale = generator._generate_rationale(item)

        assert "blocks multiple items" in rationale

    def test_generate_rationale_quick_win(self):
        """Test generating rationale for quick wins."""
        generator = ReportGenerator(Path(__file__))
        item = {
            'priority_factors': {
                'severity': 50,
                'dependencies': 0,
                'impact': 50,
                'effort': 100,
                'age': 50,
                'frequency': 25
            }
        }
        rationale = generator._generate_rationale(item)

        assert "quick win" in rationale

    def test_generate_rationale_multiple_factors(self):
        """Test generating rationale with multiple factors."""
        generator = ReportGenerator(Path(__file__))
        item = {
            'priority_factors': {
                'severity': 100,
                'dependencies': 75,
                'impact': 100,
                'effort': 75,
                'age': 85,
                'frequency': 50
            }
        }
        rationale = generator._generate_rationale(item)

        assert "critical severity" in rationale
        assert "blocks multiple items" in rationale
        assert "high impact" in rationale

    def test_format_velocity_trend_insufficient_data(self):
        """Test formatting velocity with insufficient data."""
        generator = ReportGenerator(Path(__file__))
        result = generator._format_velocity_trend([])

        assert "Insufficient" in result

    def test_format_velocity_trend_limited_data(self):
        """Test formatting velocity with limited data."""
        generator = ReportGenerator(Path(__file__))
        velocity_data = [
            {'week': '2025-W40', 'items_completed': 5, 'points_completed': 15}
        ]
        result = generator._format_velocity_trend(velocity_data)

        assert "5.0" in result
        assert "limited data" in result

    def test_format_velocity_trend_improving(self):
        """Test formatting velocity with improving trend."""
        generator = ReportGenerator(Path(__file__))
        velocity_data = [
            {'week': '2025-W38', 'items_completed': 3, 'points_completed': 9},
            {'week': '2025-W39', 'items_completed': 4, 'points_completed': 12},
            {'week': '2025-W40', 'items_completed': 5, 'points_completed': 15},
            {'week': '2025-W41', 'items_completed': 7, 'points_completed': 21},
            {'week': '2025-W42', 'items_completed': 8, 'points_completed': 24}
        ]
        result = generator._format_velocity_trend(velocity_data)

        assert "improving" in result

    def test_format_velocity_trend_declining(self):
        """Test formatting velocity with declining trend."""
        generator = ReportGenerator(Path(__file__))
        velocity_data = [
            {'week': '2025-W38', 'items_completed': 8, 'points_completed': 24},
            {'week': '2025-W39', 'items_completed': 7, 'points_completed': 21},
            {'week': '2025-W40', 'items_completed': 4, 'points_completed': 12},
            {'week': '2025-W41', 'items_completed': 3, 'points_completed': 9},
            {'week': '2025-W42', 'items_completed': 2, 'points_completed': 6}
        ]
        result = generator._format_velocity_trend(velocity_data)

        assert "declining" in result

    def test_find_best_component(self):
        """Test finding component with best velocity."""
        generator = ReportGenerator(Path(__file__))
        completion_times = {
            'core': {'mean': 8, 'median': 6, 'stdev': 2},
            'ui': {'mean': 3, 'median': 2, 'stdev': 1},
            'api': {'mean': 5, 'median': 4, 'stdev': 1}
        }
        result = generator._find_best_component(completion_times)

        assert result == 'ui'  # Lowest median time

    def test_find_best_component_empty(self):
        """Test finding best component with no data."""
        generator = ReportGenerator(Path(__file__))
        result = generator._find_best_component({})

        assert result == "N/A"

    def test_calculate_dependency_impact(self):
        """Test calculating dependency impact."""
        generator = ReportGenerator(Path(__file__))
        items = [
            {'blocking': ['FEAT-001', 'FEAT-002']},
            {'blocking': []},
            {'blocking': []},
            {'blocking': []}
        ]
        impact = generator._calculate_dependency_impact(items)

        # 1 out of 4 items has dependencies = 25% * 30 = 7.5 -> 7
        assert impact == 7

    def test_find_parallel_opportunities(self):
        """Test finding parallel work opportunities."""
        generator = ReportGenerator(Path(__file__))
        items = [
            {'id': 'BUG-001', 'title': 'Bug 1', 'dependencies': []},
            {'id': 'BUG-002', 'title': 'Bug 2', 'dependencies': []},
            {'id': 'FEAT-001', 'title': 'Feature 1', 'dependencies': ['BUG-001']}
        ]
        opportunities = generator._find_parallel_opportunities(items, {})

        assert len(opportunities) > 0
        assert any('BUG-001' in opp for opp in opportunities)
        assert any('BUG-002' in opp for opp in opportunities)

    def test_find_parallel_opportunities_none(self):
        """Test finding parallel opportunities with no options."""
        generator = ReportGenerator(Path(__file__))
        items = [
            {'id': 'BUG-001', 'title': 'Bug 1', 'dependencies': ['FEAT-001']}
        ]
        opportunities = generator._find_parallel_opportunities(items, {})

        assert "No clear parallel opportunities" in opportunities[0]

    def test_prepare_report_data(self, sample_data):
        """Test preparing data for report generation."""
        generator = ReportGenerator(Path(__file__))
        prepared = generator._prepare_report_data(sample_data)

        assert 'timestamp' in prepared
        assert 'total_items' in prepared
        assert 'top_items' in prepared
        assert 'critical_path' in prepared
        assert 'recommendations' in prepared

        assert prepared['total_items'] == 2
        assert len(prepared['top_items']) == 2
        assert 'rationale' in prepared['top_items'][0]

    def test_generate_full_report(self, temp_template, sample_data):
        """Test generating a complete report."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'report.md'

            generator = ReportGenerator(temp_template)
            generator.generate(sample_data, output_path)

            assert output_path.exists()
            content = output_path.read_text()

            assert "Priority Report" in content
            assert "BUG-001" in content
            assert "Critical Bug" in content
            assert "Focus on critical bugs first" in content

        temp_template.unlink()  # Cleanup


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
