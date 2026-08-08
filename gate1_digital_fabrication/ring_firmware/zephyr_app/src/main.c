/*
 * Edge I/O Ring — Zephyr west build smoke (nRF52840).
 * DEVELOPMENT only. PHYSICAL_EXECUTION_FREEZE: not flashed.
 */
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

int main(void)
{
	printk("edge_io_ring zephyr west build ok\n");
	while (1) {
		k_msleep(1000);
	}
	return 0;
}
