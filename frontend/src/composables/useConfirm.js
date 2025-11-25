import { Dialog } from "frappe-ui"
import { createApp } from "vue"

export function useConfirm() {
	const confirm = (message, title = "Confirm Action") => {
		return new Promise((resolve) => {
			const app = createApp({
				render() {
					return h(Dialog, {
						title,
						message,
						actions: [
							{
								label: "Cancel",
								onClick: () => {
									resolve(false)
								},
							},
							{
								label: "Confirm",
								variant: "solid",
								onClick: () => {
									resolve(true)
								},
							},
						],
					})
				},
			})

			const container = document.createElement("div")
			document.body.appendChild(container)
			app.mount(container)
		})
	}

	return { confirm }
}
