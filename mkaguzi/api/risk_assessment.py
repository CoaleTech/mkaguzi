# -*- coding: utf-8 -*-
# Copyright (c) 2025, Coale Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
import json


@frappe.whitelist()
def calculate_risk_score(entity_id, risk_factors):
	"""
	Calculate risk score based on risk factors

	Args:
		entity_id (str): ID of the entity (e.g., audit universe ID)
		risk_factors (list/dict): List of risk factors or dict with weights

	Returns:
		dict: Risk score details including overall score, rating, and breakdown
	"""
	frappe.has_permission("Risk Assessment", "read", throw=True)

	if isinstance(risk_factors, str):
		risk_factors = json.loads(risk_factors)

	# Risk scoring methodology
	# Impact: Low=1, Medium=2, High=3, Critical=4
	# Likelihood: Low=1, Medium=2, High=3, Very High=4

	total_score = 0
	max_score = 0
	factor_scores = []

	for factor in risk_factors:
		impact = factor.get("impact", "Medium")
		likelihood = factor.get("likelihood", "Medium")
		weight = factor.get("weight", 1.0)

		# Convert impact to numeric value
		impact_values = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
		impact_score = impact_values.get(impact, 2)

		# Convert likelihood to numeric value
		likelihood_values = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
		likelihood_score = likelihood_values.get(likelihood, 2)

		# Calculate weighted score
		factor_score = impact_score * likelihood_score * weight
		total_score += factor_score
		max_score += 16 * weight  # Max is 4*4=16 per factor

		factor_scores.append({
			"factor": factor.get("name", "Unknown"),
			"impact": impact,
			"likelihood": likelihood,
			"weight": weight,
			"score": factor_score
		})

	# Calculate overall score percentage
	overall_score = (total_score / max_score * 100) if max_score > 0 else 0

	# Determine risk rating
	if overall_score >= 75:
		risk_rating = "Critical"
		risk_color = "#dc2626"  # Red
	elif overall_score >= 50:
		risk_rating = "High"
		risk_color = "#f97316"  # Orange
	elif overall_score >= 25:
		risk_rating = "Medium"
		risk_color = "#eab308"  # Yellow
	else:
		risk_rating = "Low"
		risk_color = "#22c55e"  # Green

	return {
		"entity_id": entity_id,
		"overall_score": round(overall_score, 2),
		"risk_rating": risk_rating,
		"risk_color": risk_color,
		"factor_scores": factor_scores,
		"total_factors": len(risk_factors)
	}


@frappe.whitelist()
def get_risk_matrix():
	"""
	Get risk matrix data for visualization

	Returns:
		dict: Risk matrix with likelihood vs impact grid
	"""
	likelihood_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
	impact_levels = ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"]

	matrix = []
	for i, likelihood in enumerate(likelihood_levels):
		row = []
		for j, impact in enumerate(impact_levels):
			# Calculate risk score for this cell
			score = (i + 1) * (j + 1)

			# Determine rating
			if score >= 20:
				rating = "Critical"
				color = "#dc2626"
			elif score >= 12:
				rating = "High"
				color = "#f97316"
			elif score >= 6:
				rating = "Medium"
				color = "#eab308"
			else:
				rating = "Low"
				color = "#22c55e"

			row.append({
				"likelihood": likelihood,
				"impact": impact,
				"score": score,
				"rating": rating,
				"color": color
			})
		matrix.append(row)

	return {
		"likelihood_levels": likelihood_levels,
		"impact_levels": impact_levels,
		"matrix": matrix
	}


@frappe.whitelist()
def aggregate_risks_by_department(department=None):
	"""
	Aggregate risks by department/function

	Args:
		department (str): Optional department filter

	Returns:
		dict: Risk aggregation by department
	"""
	frappe.has_permission("Risk Assessment", "read", throw=True)

	filters = {"docstatus": 1}
	if department:
		filters["department"] = department

	# Get risk assessments with their scores
	assessments = frappe.get_all("Risk Assessment",
		filters=filters,
		fields=["name", "department", "overall_risk_score", "risk_rating",
			"assessment_date", "assessment_type"]
	)

	# Aggregate by department
	department_risks = {}
	for assessment in assessments:
		dept = assessment.get("department") or "Unassigned"
		if dept not in department_risks:
			department_risks[dept] = {
				"department": dept,
				"total_assessments": 0,
				"critical_count": 0,
				"high_count": 0,
				"medium_count": 0,
				"low_count": 0,
				"average_score": 0,
				"assessments": []
			}

		dept_risks = department_risks[dept]
		dept_risks["total_assessments"] += 1
		dept_risks["assessments"].append(assessment)

		rating = assessment.get("risk_rating", "")
		if rating == "Critical":
			dept_risks["critical_count"] += 1
		elif rating == "High":
			dept_risks["high_count"] += 1
		elif rating == "Medium":
			dept_risks["medium_count"] += 1
		else:
			dept_risks["low_count"] += 1

	# Calculate averages
	for dept, data in department_risks.items():
		if data["total_assessments"] > 0:
			total_score = sum(a.get("overall_risk_score", 0) for a in data["assessments"])
			data["average_score"] = round(total_score / data["total_assessments"], 2)

	return {
		"department_risks": list(department_risks.values()),
		"total_departments": len(department_risks),
		"summary": {
			"total_assessments": sum(d["total_assessments"] for d in department_risks.values()),
			"total_critical": sum(d["critical_count"] for d in department_risks.values()),
			"total_high": sum(d["high_count"] for d in department_risks.values()),
			"total_medium": sum(d["medium_count"] for d in department_risks.values()),
			"total_low": sum(d["low_count"] for d in department_risks.values())
		}
	}


@frappe.whitelist()
def get_risk_trends(period_days=90):
	"""
	Get risk trends over time

	Args:
		period_days (int): Number of days to look back

	Returns:
		dict: Risk trend data
	"""
	from frappe.utils import add_days, today

	start_date = add_days(today(), -period_days)

	assessments = frappe.get_all("Risk Assessment",
		filters={
			"assessment_date": (">=", start_date),
			"docstatus": 1
		},
		fields=["assessment_date", "overall_risk_score", "risk_rating"],
		order_by="assessment_date asc"
	)

	# Group by date
	trends = {}
	for assessment in assessments:
		date_str = str(assessment.get("assessment_date"))
		if date_str not in trends:
			trends[date_str] = {
				"date": date_str,
				"count": 0,
				"avg_score": 0,
				"critical": 0,
				"high": 0,
				"medium": 0,
				"low": 0
			}

		trends[date_str]["count"] += 1
		trends[date_str]["avg_score"] += assessment.get("overall_risk_score", 0)

		rating = assessment.get("risk_rating", "")
		if rating == "Critical":
			trends[date_str]["critical"] += 1
		elif rating == "High":
			trends[date_str]["high"] += 1
		elif rating == "Medium":
			trends[date_str]["medium"] += 1
		else:
			trends[date_str]["low"] += 1

	# Calculate averages
	for trend in trends.values():
		if trend["count"] > 0:
			trend["avg_score"] = round(trend["avg_score"] / trend["count"], 2)

	return {
		"trends": sorted(trends.values(), key=lambda x: x["date"]),
		"period_days": period_days
	}


@frappe.whitelist()
def get_top_risks(limit=10):
	"""
	Get top risks by score

	Args:
		limit (int): Number of top risks to return

	Returns:
		list: Top risk items
	"""
	frappe.has_permission("Risk Assessment", "read", throw=True)

	risks = frappe.get_all("Risk Assessment",
		filters={"docstatus": 1},
		fields=["name", "assessment_name", "department", "overall_risk_score",
			"risk_rating", "assessment_date"],
		order_by="overall_risk_score desc",
		limit=limit
	)

	return risks


@frappe.whitelist()
def create_risk_assessment(assessment_name, department, risk_factors, assessment_type="Traditional"):
	"""
	Create a new risk assessment

	Args:
		assessment_name (str): Name of the assessment
		department (str): Department name
		risk_factors (list): List of risk factors
		assessment_type (str): Type of assessment

	Returns:
		dict: Success status and details
	"""
	frappe.has_permission("Risk Assessment", "create", throw=True)

	if isinstance(risk_factors, str):
		risk_factors = json.loads(risk_factors)

	# Calculate risk score
	score_result = calculate_risk_score(department, risk_factors)

	doc = frappe.get_doc({
		"doctype": "Risk Assessment",
		"assessment_name": assessment_name,
		"department": department,
		"assessment_type": assessment_type,
		"assessment_date": getdate(),
		"overall_risk_score": score_result["overall_score"],
		"risk_rating": score_result["risk_rating"],
		"risk_factors": risk_factors
	})
	doc.insert()

	return {
		"success": True,
		"message": _("Risk Assessment created successfully"),
		"name": doc.name,
		"risk_score": score_result
	}


@frappe.whitelist()
def update_risk_assessment(assessment_id, risk_factors=None, **kwargs):
	"""
	Update an existing risk assessment

	Args:
		assessment_id (str): ID of the assessment
		risk_factors (list): Updated risk factors
		**kwargs: Other fields to update

	Returns:
		dict: Success status and updated details
	"""
	frappe.has_permission("Risk Assessment", "write", throw=True)

	doc = frappe.get_doc("Risk Assessment", assessment_id)

	if risk_factors:
		if isinstance(risk_factors, str):
			risk_factors = json.loads(risk_factors)

		doc.risk_factors = risk_factors

		# Recalculate score
		score_result = calculate_risk_score(doc.department, risk_factors)
		doc.overall_risk_score = score_result["overall_score"]
		doc.risk_rating = score_result["risk_rating"]

	for field, value in kwargs.items():
		if hasattr(doc, field):
			setattr(doc, field, value)

	doc.save()

	return {
		"success": True,
		"message": _("Risk Assessment updated successfully"),
		"name": doc.name
	}


@frappe.whitelist()
def get_risk_assessment_summary():
	"""
	Get summary statistics for risk assessments

	Returns:
		dict: Summary statistics
	"""
	total = frappe.db.count("Risk Assessment", {"docstatus": 1})

	summary = frappe.db.sql("""
		SELECT
			risk_rating,
			COUNT(*) as count
		FROM `tabRisk Assessment`
		WHERE docstatus = 1
		GROUP BY risk_rating
	""", as_dict=True)

	rating_counts = {s["risk_rating"]: s["count"] for s in summary}

	avg_score = frappe.db.sql("""
		SELECT AVG(overall_risk_score) as avg_score
		FROM `tabRisk Assessment`
		WHERE docstatus = 1
	""", as_dict=True)[0]["avg_score"] or 0

	return {
		"total_assessments": total,
		"critical_count": rating_counts.get("Critical", 0),
		"high_count": rating_counts.get("High", 0),
		"medium_count": rating_counts.get("Medium", 0),
		"low_count": rating_counts.get("Low", 0),
		"average_score": round(avg_score, 2)
	}
