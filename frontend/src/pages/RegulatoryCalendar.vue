<template>
  <div class="regulatory-calendar-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <Calendar class="title-icon" />
          Regulatory Calendar 2025
        </h1>
        <p class="page-description">
          Comprehensive Kenyan tax compliance calendar with all statutory deadlines and payment requirements
        </p>
      </div>
      <div class="header-actions">
        <Button variant="outline" @click="exportCalendar">
          <Download />
          Export Calendar
        </Button>
        <Button variant="outline" @click="printCalendar">
          <Printer />
          Print Calendar
        </Button>
      </div>
    </div>

    <!-- Important Notice -->
    <div class="notice-section">
      <div class="notice-card">
        <AlertTriangle class="notice-icon" />
        <div class="notice-content">
          <h3>General Ongoing Rule</h3>
          <p><strong>DAT, WHT, and WH VAT:</strong> Payments must be made within 5 working days after making the deduction or accrual.</p>
        </div>
      </div>
    </div>

    <!-- Calendar Navigation -->
    <div class="calendar-navigation">
      <div class="nav-controls">
        <Button
          variant="outline"
          size="sm"
          @click="previousMonth"
          :disabled="currentMonth === 0"
        >
          <ChevronLeft />
          Previous
        </Button>
        <h2 class="current-month">{{ monthNames[currentMonth] }} 2025</h2>
        <Button
          variant="outline"
          size="sm"
          @click="nextMonth"
          :disabled="currentMonth === 11"
        >
          Next
          <ChevronRight />
        </Button>
      </div>
      <div class="month-selector">
        <Select
          v-model="currentMonth"
          :options="monthOptions"
          @change="updateCalendar"
        />
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="calendar-container">
      <!-- Calendar Header -->
      <div class="calendar-header">
        <div v-for="day in dayNames" :key="day" class="header-day">
          {{ day }}
        </div>
      </div>

      <!-- Calendar Body -->
      <div class="calendar-body">
        <!-- Empty cells for days before the first day of the month -->
        <div
          v-for="empty in firstDayOfMonth"
          :key="'empty-' + empty"
          class="calendar-day empty"
        ></div>

        <!-- Calendar days -->
        <div
          v-for="day in daysInMonth"
          :key="day"
          :class="[
            'calendar-day',
            { 'has-events': getDayEvents(day).length > 0 },
            { 'today': isToday(day) }
          ]"
          @click="selectDay(day)"
        >
          <div class="day-number">{{ day }}</div>
          <div class="day-events">
            <div
              v-for="event in getDayEvents(day).slice(0, 2)"
              :key="event.id"
              :class="['event-item', getEventTypeClass(event.type)]"
              :title="event.description"
            >
              {{ event.title }}
            </div>
            <div
              v-if="getDayEvents(day).length > 2"
              class="event-more"
            >
              +{{ getDayEvents(day).length - 2 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Day Details -->
    <div v-if="selectedDay" class="day-details-section">
      <div class="day-details-header">
        <h3>{{ monthNames[currentMonth] }} {{ selectedDay }}, 2025</h3>
        <Button variant="ghost" @click="selectedDay = null">
          <X />
        </Button>
      </div>

      <div v-if="getDayEvents(selectedDay).length === 0" class="no-events">
        <Calendar class="no-events-icon" />
        <p>No regulatory deadlines on this date</p>
      </div>

      <div v-else class="events-list">
        <div
          v-for="event in getDayEvents(selectedDay)"
          :key="event.id"
          :class="['event-detail-card', getEventTypeClass(event.type)]"
        >
          <div class="event-header">
            <div class="event-icon">
              <component :is="getEventIcon(event.type)" />
            </div>
            <div class="event-meta">
              <h4>{{ event.title }}</h4>
              <Badge :variant="getEventTypeVariant(event.type)">
                {{ event.type }}
              </Badge>
            </div>
          </div>
          <div class="event-description">
            {{ event.description }}
          </div>
          <div v-if="event.details" class="event-details">
            <div v-for="detail in event.details" :key="detail" class="event-detail-item">
              • {{ detail }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend-section">
      <h3>Legend</h3>
      <div class="legend-grid">
        <div class="legend-item">
          <div class="legend-color paye"></div>
          <span>PAYE</span>
        </div>
        <div class="legend-item">
          <div class="legend-color vat"></div>
          <span>VAT & Other Taxes</span>
        </div>
        <div class="legend-item">
          <div class="legend-color corporate"></div>
          <span>Corporate Income Tax</span>
        </div>
        <div class="legend-item">
          <div class="legend-color social"></div>
          <span>Social Security & NSSF</span>
        </div>
        <div class="legend-item">
          <div class="legend-color levy"></div>
          <span>Levies & Other</span>
        </div>
        <div class="legend-item">
          <div class="legend-color helb"></div>
          <span>HELB</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, Select } from "frappe-ui"
import {
	AlertTriangle,
	Building,
	Calculator,
	Calendar,
	ChevronLeft,
	ChevronRight,
	Clock,
	DollarSign,
	Download,
	FileText,
	Printer,
	Users,
	X,
} from "lucide-vue-next"
import { computed, onMounted, ref } from "vue"

// Reactive data
const currentMonth = ref(new Date().getMonth())
const selectedDay = ref(null)

// Calendar data for 2025
const monthNames = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
]

const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

// Regulatory events data
const regulatoryEvents = ref([
	// January 2025
	{
		id: 1,
		month: 0,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for December 2024",
		details: ["Monthly PAYE returns", "PAYE tax payments"],
	},
	{
		id: 2,
		month: 0,
		day: 9,
		type: "Social",
		title: "NSSF Payments",
		description: "NSSF payments for December 2024",
	},
	{
		id: 3,
		month: 0,
		day: 9,
		type: "Levy",
		title: "SHIF Payments",
		description: "SHIF payments for December 2024",
	},
	{
		id: 4,
		month: 0,
		day: 9,
		type: "Levy",
		title: "Catering Levy",
		description: "Catering levy returns and payment for December 2024",
	},
	{
		id: 5,
		month: 0,
		day: 9,
		type: "Levy",
		title: "NITA Levy",
		description: "NITA Levy for December 2024",
	},
	{
		id: 6,
		month: 0,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "Affordable Housing Levy (AHL) payments for December 2024",
	},
	{
		id: 7,
		month: 0,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for December 2024",
	},
	{
		id: 8,
		month: 0,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for December 2024",
	},
	{
		id: 9,
		month: 0,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments (for relevant year-ends)",
	},
	{
		id: 10,
		month: 0,
		day: 31,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description: "Submit Corporate Income Tax returns for July 2024 year-ends",
	},
	{
		id: 11,
		month: 0,
		day: 31,
		type: "Corporate",
		title: "Transfer Pricing Documents",
		description:
			"Submit Transfer Pricing Master/Local File for July 2024 year-ends",
	},
	{
		id: 12,
		month: 0,
		day: 31,
		type: "Corporate",
		title: "CbC Report",
		description:
			"Submit Country by Country (CbC) Report for January 2024 year-ends",
	},
	{
		id: 13,
		month: 0,
		day: 31,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for September 2024 year-ends",
	},

	// February 2025
	{
		id: 14,
		month: 1,
		day: 7,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for January 2025",
	},
	{
		id: 15,
		month: 1,
		day: 7,
		type: "Social",
		title: "SHIF, NSSF & Levies",
		description: "SHIF, NSSF, Catering levy, and NITA Levy for January 2025",
	},
	{
		id: 16,
		month: 1,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for January 2025",
	},
	{
		id: 17,
		month: 1,
		day: 14,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for January 2025",
	},
	{
		id: 18,
		month: 1,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 19,
		month: 1,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for January 2025",
	},
	{
		id: 20,
		month: 1,
		day: 28,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax Returns for August 2024 year-ends",
	},
	{
		id: 21,
		month: 1,
		day: 28,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 22,
		month: 1,
		day: 28,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for October 2024 year-ends",
	},

	// March 2025
	{
		id: 23,
		month: 2,
		day: 7,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for February 2025",
	},
	{
		id: 24,
		month: 2,
		day: 7,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for February 2025",
	},
	{
		id: 25,
		month: 2,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for February 2025",
	},
	{
		id: 26,
		month: 2,
		day: 14,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for February 2025",
	},
	{
		id: 27,
		month: 2,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 28,
		month: 2,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for February 2025",
	},
	{
		id: 29,
		month: 2,
		day: 31,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax returns for September 2024 year-ends",
	},
	{
		id: 30,
		month: 2,
		day: 31,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 31,
		month: 2,
		day: 31,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for November 2024 year-ends",
	},

	// April 2025
	{
		id: 32,
		month: 3,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for March 2025",
	},
	{
		id: 33,
		month: 3,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for March 2025",
	},
	{
		id: 34,
		month: 3,
		day: 11,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for March 2025",
	},
	{
		id: 35,
		month: 3,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for March 2025",
	},
	{
		id: 36,
		month: 3,
		day: 17,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for March 2025",
	},
	{
		id: 37,
		month: 3,
		day: 17,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 38,
		month: 3,
		day: 17,
		type: "PAYE",
		title: "Individual Instalment Tax",
		description:
			"First instalment tax payment for individuals (2025 year of income)",
	},
	{
		id: 39,
		month: 3,
		day: 30,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax returns for October 2024 year-ends",
	},
	{
		id: 40,
		month: 3,
		day: 30,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 41,
		month: 3,
		day: 30,
		type: "PAYE",
		title: "Individual Tax Balance",
		description: "Individuals: Pay balance of tax for 2024 year of income",
	},

	// May 2025
	{
		id: 42,
		month: 4,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for April 2025",
	},
	{
		id: 43,
		month: 4,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for April 2025",
	},
	{
		id: 44,
		month: 4,
		day: 14,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for April 2025",
	},
	{
		id: 45,
		month: 4,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for April 2025",
	},
	{
		id: 46,
		month: 4,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 47,
		month: 4,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for April 2025",
	},
	{
		id: 48,
		month: 4,
		day: 30,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax Returns for November 2024 year-ends",
	},
	{
		id: 49,
		month: 4,
		day: 30,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 50,
		month: 4,
		day: 30,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for January 2025 year-ends",
	},

	// June 2025
	{
		id: 51,
		month: 5,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for May 2025",
	},
	{
		id: 52,
		month: 5,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for May 2025",
	},
	{
		id: 53,
		month: 5,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for May 2025",
	},
	{
		id: 54,
		month: 5,
		day: 13,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for May 2025",
	},
	{
		id: 55,
		month: 5,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 56,
		month: 5,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for May 2025",
	},
	{
		id: 57,
		month: 5,
		day: 20,
		type: "PAYE",
		title: "Individual Instalment Tax",
		description:
			"Second instalment tax payment for individuals (2025 year of income)",
	},
	{
		id: 58,
		month: 5,
		day: 30,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax Returns for December 2024 year-ends",
	},
	{
		id: 59,
		month: 5,
		day: 30,
		type: "PAYE",
		title: "Individual Income Tax Returns",
		description: "Individuals: Submit income tax returns for year 2024",
	},
	{
		id: 60,
		month: 5,
		day: 30,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 61,
		month: 5,
		day: 30,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for February 2025 year-ends",
	},

	// July 2025
	{
		id: 62,
		month: 6,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for June 2025",
	},
	{
		id: 63,
		month: 6,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for June 2025",
	},
	{
		id: 64,
		month: 6,
		day: 11,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for June 2025",
	},
	{
		id: 65,
		month: 6,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for June 2025",
	},
	{
		id: 66,
		month: 6,
		day: 18,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for June 2025",
	},
	{
		id: 67,
		month: 6,
		day: 18,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments (for relevant year-ends)",
	},
	{
		id: 68,
		month: 6,
		day: 31,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax returns for January 2025 year-ends",
	},
	{
		id: 69,
		month: 6,
		day: 31,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 70,
		month: 6,
		day: 31,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for March 2025 year-ends",
	},

	// August 2025
	{
		id: 71,
		month: 7,
		day: 8,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for July 2025",
	},
	{
		id: 72,
		month: 7,
		day: 8,
		type: "Social",
		title: "SHIF, NSSF & Levies",
		description: "SHIF, NSSF, Catering levy, and NITA Levy for July 2025",
	},
	{
		id: 73,
		month: 7,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for July 2025",
	},
	{
		id: 74,
		month: 7,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for July 2025",
	},
	{
		id: 75,
		month: 7,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 76,
		month: 7,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for July 2025",
	},
	{
		id: 77,
		month: 7,
		day: 29,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description:
			"Submit Corporate Income Tax returns for February 2025 year-ends",
	},
	{
		id: 78,
		month: 7,
		day: 29,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 79,
		month: 7,
		day: 29,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for April 2025 year-ends",
	},

	// September 2025
	{
		id: 80,
		month: 8,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for August 2025",
	},
	{
		id: 81,
		month: 8,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for August 2025",
	},
	{
		id: 82,
		month: 8,
		day: 11,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for August 2025",
	},
	{
		id: 83,
		month: 8,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for August 2025",
	},
	{
		id: 84,
		month: 8,
		day: 19,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 85,
		month: 8,
		day: 19,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for August 2025",
	},
	{
		id: 86,
		month: 8,
		day: 19,
		type: "PAYE",
		title: "Individual Instalment Tax",
		description:
			"Third instalment tax payment for individuals (2025 year of income)",
	},
	{
		id: 87,
		month: 8,
		day: 30,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description: "Submit Corporate Income Tax returns for March 2025 year-ends",
	},
	{
		id: 88,
		month: 8,
		day: 30,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 89,
		month: 8,
		day: 30,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for May 2025 year-ends",
	},

	// October 2025
	{
		id: 90,
		month: 9,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for September 2025",
	},
	{
		id: 91,
		month: 9,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for September 2025",
	},
	{
		id: 92,
		month: 9,
		day: 14,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for September 2025",
	},
	{
		id: 93,
		month: 9,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for September 2025",
	},
	{
		id: 94,
		month: 9,
		day: 17,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 95,
		month: 9,
		day: 17,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for September 2025",
	},
	{
		id: 96,
		month: 9,
		day: 31,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description: "Submit Corporate Income Tax returns for April 2025 year-ends",
	},
	{
		id: 97,
		month: 9,
		day: 31,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 98,
		month: 9,
		day: 31,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for June 2025 year-ends",
	},

	// November 2025
	{
		id: 99,
		month: 10,
		day: 7,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for October 2025",
	},
	{
		id: 100,
		month: 10,
		day: 7,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for October 2025",
	},
	{
		id: 101,
		month: 10,
		day: 13,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for October 2025",
	},
	{
		id: 102,
		month: 10,
		day: 14,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for October 2025",
	},
	{
		id: 103,
		month: 10,
		day: 20,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 104,
		month: 10,
		day: 20,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for October 2025",
	},
	{
		id: 105,
		month: 10,
		day: 28,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description: "Submit Corporate Income Tax returns for May 2025 year-ends",
	},
	{
		id: 106,
		month: 10,
		day: 28,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 107,
		month: 10,
		day: 28,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for July 2025 year-ends",
	},

	// December 2025
	{
		id: 108,
		month: 11,
		day: 9,
		type: "PAYE",
		title: "PAYE Payments & Returns",
		description: "PAYE payments and returns for November 2025",
	},
	{
		id: 109,
		month: 11,
		day: 9,
		type: "Social",
		title: "NSSF, SHIF & Levies",
		description: "NSSF, SHIF, Catering levy, and NITA Levy for November 2025",
	},
	{
		id: 110,
		month: 11,
		day: 11,
		type: "Levy",
		title: "AHL Payments",
		description: "AHL payments for November 2025",
	},
	{
		id: 111,
		month: 11,
		day: 15,
		type: "HELB",
		title: "HELB Payments",
		description: "HELB payments for November 2025",
	},
	{
		id: 112,
		month: 11,
		day: 19,
		type: "Corporate",
		title: "Instalment Tax Payments",
		description: "Instalment tax payments",
	},
	{
		id: 113,
		month: 11,
		day: 19,
		type: "VAT",
		title: "VAT & Tax Returns",
		description:
			"Submit returns and pay VAT, Excise Duty, RRI, SEPT, and Turnover tax for November 2025",
	},
	{
		id: 114,
		month: 11,
		day: 19,
		type: "PAYE",
		title: "Individual Instalment Tax",
		description:
			"Fourth instalment tax payment for individuals (2025 year of income)",
	},
	{
		id: 115,
		month: 11,
		day: 31,
		type: "Corporate",
		title: "Corporate Income Tax Returns",
		description: "Submit Corporate Income Tax returns for June 2025 year-ends",
	},
	{
		id: 116,
		month: 11,
		day: 31,
		type: "Corporate",
		title: "Transfer Pricing/CbC",
		description: "Submit Transfer Pricing/CbC documents for relevant year-ends",
	},
	{
		id: 117,
		month: 11,
		day: 31,
		type: "Corporate",
		title: "Tax Balance Payment",
		description: "Pay balance of tax for August 2025 year-ends",
	},
])

// Computed properties
const daysInMonth = computed(() => {
	return new Date(2025, currentMonth.value + 1, 0).getDate()
})

const firstDayOfMonth = computed(() => {
	return new Date(2025, currentMonth.value, 1).getDay()
})

const currentMonthEvents = computed(() => {
	return regulatoryEvents.value.filter(
		(event) => event.month === currentMonth.value,
	)
})

const monthOptions = computed(() => {
	return monthNames.map((month, index) => ({
		label: `${month} 2025`,
		value: index,
	}))
})

// Methods
const getDayEvents = (day) => {
	return currentMonthEvents.value.filter((event) => event.day === day)
}

const selectDay = (day) => {
	selectedDay.value = selectedDay.value === day ? null : day
}

const isToday = (day) => {
	const today = new Date()
	return (
		today.getFullYear() === 2025 &&
		today.getMonth() === currentMonth.value &&
		today.getDate() === day
	)
}

const previousMonth = () => {
	if (currentMonth.value > 0) {
		currentMonth.value--
		selectedDay.value = null
	}
}

const nextMonth = () => {
	if (currentMonth.value < 11) {
		currentMonth.value++
		selectedDay.value = null
	}
}

const updateCalendar = () => {
	selectedDay.value = null
}

const getEventTypeClass = (type) => {
	const classes = {
		PAYE: "paye",
		VAT: "vat",
		Corporate: "corporate",
		Social: "social",
		Levy: "levy",
		HELB: "helb",
	}
	return classes[type] || "default"
}

const getEventTypeVariant = (type) => {
	const variants = {
		PAYE: "blue",
		VAT: "green",
		Corporate: "purple",
		Social: "orange",
		Levy: "gray",
		HELB: "red",
	}
	return variants[type] || "gray"
}

const getEventIcon = (type) => {
	const icons = {
		PAYE: Calculator,
		VAT: DollarSign,
		Corporate: Building,
		Social: Users,
		Levy: FileText,
		HELB: Clock,
	}
	return icons[type] || FileText
}

const exportCalendar = () => {
	// Implementation for exporting calendar
	console.log("Export calendar functionality")
}

const printCalendar = () => {
	// Implementation for printing calendar
	window.print()
}

// Lifecycle
onMounted(() => {
	// Set current month to current date if it's 2025
	const today = new Date()
	if (today.getFullYear() === 2025) {
		currentMonth.value = today.getMonth()
	}
})
</script>

<style scoped>
.regulatory-calendar-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header-content h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.title-icon {
  color: var(--primary-color);
}

.page-description {
  color: var(--text-muted);
  margin: 0.5rem 0 0 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.notice-section {
  margin-bottom: 2rem;
}

.notice-card {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.notice-icon {
  color: #f59e0b;
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.notice-content h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #92400e;
  margin: 0 0 0.5rem 0;
}

.notice-content p {
  color: #92400e;
  margin: 0;
  font-size: 0.875rem;
}

.calendar-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-month {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  min-width: 150px;
  text-align: center;
}

.month-selector {
  min-width: 200px;
}

.calendar-container {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 2rem;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
}

.header-day {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
  min-height: 120px;
  padding: 0.5rem;
  border-right: 1px solid var(--border-color-2);
  border-bottom: 1px solid var(--border-color-2);
  position: relative;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.calendar-day:hover {
  background: var(--background-color);
}

.calendar-day.empty {
  background: var(--background-color);
  cursor: default;
}

.calendar-day.has-events {
  background: #f0f9ff;
}

.calendar-day.today {
  background: #dbeafe;
  border: 2px solid var(--primary-color);
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day:nth-last-child(-n+7) {
  border-bottom: none;
}

.day-number {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.event-item {
  font-size: 0.75rem;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  color: white;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-item.paye {
  background: #3b82f6;
}

.event-item.vat {
  background: #10b981;
}

.event-item.corporate {
  background: #8b5cf6;
}

.event-item.social {
  background: #f59e0b;
}

.event-item.levy {
  background: #6b7280;
}

.event-item.helb {
  background: #ef4444;
}

.event-more {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

.day-details-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.day-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.day-details-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.no-events {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.no-events-icon {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.no-events p {
  color: var(--text-muted);
  margin: 0;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.event-detail-card {
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1rem;
  background: var(--background-color);
}

.event-detail-card.paye {
  border-left: 4px solid #3b82f6;
}

.event-detail-card.vat {
  border-left: 4px solid #10b981;
}

.event-detail-card.corporate {
  border-left: 4px solid #8b5cf6;
}

.event-detail-card.social {
  border-left: 4px solid #f59e0b;
}

.event-detail-card.levy {
  border-left: 4px solid #6b7280;
}

.event-detail-card.helb {
  border-left: 4px solid #ef4444;
}

.event-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.event-icon {
  font-size: 1.25rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.event-meta {
  flex: 1;
}

.event-meta h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.25rem 0;
}

.event-description {
  color: var(--text-color);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.event-details {
  border-top: 1px solid var(--border-color-2);
  padding-top: 0.75rem;
}

.event-detail-item {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.event-detail-item:last-child {
  margin-bottom: 0;
}

.legend-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.legend-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1rem 0;
}

.legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
}

.legend-color.paye {
  background: #3b82f6;
}

.legend-color.vat {
  background: #10b981;
}

.legend-color.corporate {
  background: #8b5cf6;
}

.legend-color.social {
  background: #f59e0b;
}

.legend-color.levy {
  background: #6b7280;
}

.legend-color.helb {
  background: #ef4444;
}

.legend-item span {
  font-size: 0.875rem;
  color: var(--text-color);
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: stretch;
  }

  .calendar-navigation {
    flex-direction: column;
    gap: 1rem;
  }

  .nav-controls {
    width: 100%;
    justify-content: space-between;
  }

  .calendar-day {
    min-height: 100px;
    padding: 0.25rem;
  }

  .day-number {
    font-size: 0.75rem;
  }

  .event-item {
    font-size: 0.7rem;
    padding: 0.1rem 0.2rem;
  }

  .legend-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .day-details-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .calendar-header,
  .calendar-body {
    grid-template-columns: repeat(7, minmax(40px, 1fr));
  }

  .header-day {
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .calendar-day {
    min-height: 80px;
  }

  .legend-grid {
    grid-template-columns: 1fr;
  }
}
</style>