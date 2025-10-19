#!/usr/bin/env python3
"""
Report generator for Intelligent Priority Manager.
Processes Handlebars-like templates with priority data.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import re


class TemplateRenderer:
    """Simple Handlebars-like template renderer."""

    def __init__(self, template_content: str):
        self.template = template_content

    def render(self, data: Dict[str, Any]) -> str:
        """Render template with provided data."""
        result = self.template

        # Process #each blocks first
        result = self._process_each_blocks(result, data)

        # Process #if blocks
        result = self._process_if_blocks(result, data)

        # Process simple variables
        result = self._process_variables(result, data)

        return result

    def _process_each_blocks(self, content: str, data: Dict) -> str:
        """Process {{#each array}} blocks."""
        # Pattern: {{#each key}}...{{/each}}
        pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'

        def replace_each(match):
            key = match.group(1)
            block_content = match.group(2)

            if key not in data or not isinstance(data[key], list):
                return ''

            rendered_items = []
            for item in data[key]:
                # Replace {{this.property}} with actual values
                item_content = block_content
                item_content = self._process_this_references(item_content, item)
                rendered_items.append(item_content)

            return '\n'.join(rendered_items)

        return re.sub(pattern, replace_each, content, flags=re.DOTALL)

    def _process_this_references(self, content: str, item: Any) -> str:
        """Replace {{this.property}} references with actual values."""
        if isinstance(item, dict):
            # Handle nested properties like {{this.priority_factors.severity}}
            pattern = r'\{\{this\.([a-zA-Z0-9_.]+)\}\}'

            def replace_property(match):
                prop_path = match.group(1).split('.')
                value = item

                for prop in prop_path:
                    if isinstance(value, dict) and prop in value:
                        value = value[prop]
                    else:
                        return ''

                return str(value)

            return re.sub(pattern, replace_property, content)
        else:
            # Simple value
            return content.replace('{{this}}', str(item))

    def _process_if_blocks(self, content: str, data: Dict) -> str:
        """Process {{#if key}}...{{else}}...{{/if}} blocks."""
        # Pattern: {{#if key}}...{{else}}...{{/if}}
        pattern = r'\{\{#if\s+(\w+)\}\}(.*?)(?:\{\{else\}\}(.*?))?\{\{/if\}\}'

        def replace_if(match):
            key = match.group(1)
            true_content = match.group(2)
            false_content = match.group(3) if match.group(3) else ''

            if key in data and data[key]:
                return true_content
            else:
                return false_content

        return re.sub(pattern, replace_if, content, flags=re.DOTALL)

    def _process_variables(self, content: str, data: Dict) -> str:
        """Replace simple {{variable}} references."""
        pattern = r'\{\{(\w+)\}\}'

        def replace_var(match):
            key = match.group(1)
            if key in data:
                return str(data[key])
            return match.group(0)  # Leave unchanged if not found

        return re.sub(pattern, replace_var, content)


class ReportGenerator:
    """Generates priority reports from analysis data."""

    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.template_content = template_path.read_text()
        self.renderer = TemplateRenderer(self.template_content)

    def generate(self, data: Dict, output_path: Path) -> None:
        """Generate report from data and save to output path."""
        # Prepare report data
        report_data = self._prepare_report_data(data)

        # Render template
        report_content = self.renderer.render(report_data)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)

        print(f"✅ Report generated: {output_path}")

    def _prepare_report_data(self, data: Dict) -> Dict:
        """Prepare data for template rendering."""
        items = data.get('items', [])
        dependencies = data.get('dependencies', {})
        patterns = data.get('patterns', {})

        # Calculate executive summary stats
        ready_items = [item for item in items if not item.get('blocked', False)]
        blocked_items = [item for item in items if item.get('blocked', False)]

        # Get top items (first 5 highest priority)
        top_items = items[:5] if len(items) > 5 else items

        # Add rationale to each item
        for item in top_items:
            item['rationale'] = self._generate_rationale(item)

        # Format critical path
        critical_path = dependencies.get('critical_path', [])
        critical_path_str = ' → '.join(critical_path) if critical_path else 'No critical path found'

        # Check for circular dependencies
        circular_deps = dependencies.get('circular_dependencies', [])
        circular_deps_formatted = [' → '.join(cycle) for cycle in circular_deps] if circular_deps else None

        # Calculate historical insights
        velocity_summary = self._format_velocity_trend(patterns.get('velocity_trend', []))

        completion_times = patterns.get('completion_time_by_component', {})
        component_with_best_velocity = self._find_best_component(completion_times)

        effort_accuracy_data = patterns.get('effort_accuracy', {})
        effort_accuracy = abs(effort_accuracy_data.get('mean_error', 0))

        # Calculate dependency impact (items with deps vs without)
        dependency_impact = self._calculate_dependency_impact(items)

        # Get recommendations
        recommendations = data.get('recommendations', [])

        # Find parallel work opportunities
        parallel_opportunities = self._find_parallel_opportunities(items, dependencies)

        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_type': data.get('analysis_type', 'Full Priority Analysis'),
            'total_items': len(items),
            'critical_path_length': len(critical_path),
            'ready_count': len(ready_items),
            'blocked_count': len(blocked_items),
            'top_items': top_items,
            'critical_path': critical_path_str,
            'circular_dependencies': circular_deps_formatted,
            'velocity_summary': velocity_summary,
            'dependency_impact': dependency_impact,
            'component_with_best_velocity': component_with_best_velocity,
            'effort_accuracy': f"{effort_accuracy:.1f}",
            'recommendations': recommendations,
            'parallel_opportunities': parallel_opportunities
        }

    def _generate_rationale(self, item: Dict) -> str:
        """Generate human-readable rationale for item's priority."""
        factors = item.get('priority_factors', {})
        reasons = []

        severity_score = factors.get('severity', 0)
        if severity_score >= 75:
            reasons.append("critical severity")

        dep_score = factors.get('dependencies', 0)
        if dep_score >= 75:
            reasons.append("blocks multiple items")

        impact_score = factors.get('impact', 0)
        if impact_score >= 75:
            reasons.append("high impact on critical components")

        effort_score = factors.get('effort', 0)
        if effort_score >= 75:
            reasons.append("quick win opportunity")

        age_score = factors.get('age', 0)
        if age_score >= 80:
            reasons.append("long-standing issue")

        if not reasons:
            reasons.append("balanced priority factors")

        return f"Prioritized due to {', '.join(reasons)}"

    def _format_velocity_trend(self, velocity_data: List[Dict]) -> str:
        """Format velocity trend for display."""
        if not velocity_data:
            return "Insufficient historical data"

        if len(velocity_data) < 3:
            avg_items = sum(v['items_completed'] for v in velocity_data) / len(velocity_data)
            return f"Current velocity: {avg_items:.1f} items/week (limited data)"

        recent_weeks = velocity_data[-3:]
        avg_recent = sum(v['items_completed'] for v in recent_weeks) / 3

        older_weeks = velocity_data[-6:-3] if len(velocity_data) >= 6 else velocity_data[:-3]
        avg_older = sum(v['items_completed'] for v in older_weeks) / len(older_weeks) if older_weeks else avg_recent

        trend = "stable"
        if avg_recent > avg_older * 1.2:
            trend = "improving"
        elif avg_recent < avg_older * 0.8:
            trend = "declining"

        return f"Current velocity: {avg_recent:.1f} items/week (trend: {trend})"

    def _find_best_component(self, completion_times: Dict) -> str:
        """Find component with best (fastest) completion time."""
        if not completion_times:
            return "N/A"

        best_component = None
        best_time = float('inf')

        for component, stats in completion_times.items():
            median_time = stats.get('median', float('inf'))
            if median_time < best_time:
                best_time = median_time
                best_component = component

        return best_component if best_component else "N/A"

    def _calculate_dependency_impact(self, items: List[Dict]) -> int:
        """Calculate percentage impact of dependencies on completion time."""
        # Simplified calculation - in reality would use historical data
        items_with_deps = [item for item in items if item.get('blocking', [])]

        if not items:
            return 0

        # Estimate: items with dependencies take ~30% longer on average
        percentage = min(int((len(items_with_deps) / len(items)) * 30), 100)
        return percentage

    def _find_parallel_opportunities(self, items: List[Dict], dependencies: Dict) -> List[str]:
        """Identify items that can be worked on in parallel."""
        # Get items with no dependencies
        independent_items = []

        for item in items[:10]:  # Check top 10 items
            item_id = item.get('id', '')
            has_deps = bool(item.get('dependencies', []))

            if not has_deps:
                independent_items.append(f"{item_id}: {item.get('title', 'Untitled')}")

        if len(independent_items) >= 2:
            return independent_items[:3]  # Return top 3
        else:
            return ["No clear parallel opportunities at this time"]


def main():
    parser = argparse.ArgumentParser(description='Generate priority reports')
    parser.add_argument('--template', required=True, help='Path to report template')
    parser.add_argument('--data', required=True, help='Path to priority data JSON')
    parser.add_argument('--output', required=True, help='Output path for report')

    args = parser.parse_args()

    template_path = Path(args.template)
    data_path = Path(args.data)
    output_path = Path(args.output)

    # Load data
    with open(data_path) as f:
        data = json.load(f)

    # Generate report
    generator = ReportGenerator(template_path)
    generator.generate(data, output_path)

    print(f"✅ Report successfully generated at {output_path}")


if __name__ == '__main__':
    main()
