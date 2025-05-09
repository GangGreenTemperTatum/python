import time
from zapv2 import ZAPv2
from datetime import datetime

# --- Configuration ---
# ZAP Connection Details
ZAP_ADDRESS = "http://localhost"  # Or your ZAP's IP/hostname
ZAP_PORT = "8081"  # Or your ZAP's port
ZAP_API_KEY = "YOUR_ZAP_API_KEY"  # Replace with your ZAP API key if you have one set, otherwise leave as '' or None

# Target Details
TARGET_URL = "http://localhost:3000"  # !!! REPLACE WITH YOUR TARGET URL !!!
# Ensure the TARGET_URL is the base URL you want to scan (e.g., http://, https://public-website.com)

CONTEXT_NAME_PREFIX = "AutoContext_"
# --- End Configuration ---


def main():
    zap_proxy = {
        "http": f"{ZAP_ADDRESS}:{ZAP_PORT}",
        "https": f"{ZAP_ADDRESS}:{ZAP_PORT}",
    }

    try:
        zap = ZAPv2(apikey=ZAP_API_KEY, proxies=zap_proxy)
        # Test connection
        print(f"Successfully connected to ZAP version: {zap.core.version}")
    except Exception as e:
        print(f"Error connecting to ZAP API: {e}")
        print(
            f"Please ensure ZAP is running at {ZAP_ADDRESS}:{ZAP_PORT} and the API key (if used) is correct."
        )
        return

    # Generate a unique context name using a timestamp
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    context_name = f"{CONTEXT_NAME_PREFIX}{timestamp_str}"
    target_regex = TARGET_URL + ".*"  # Regex to include everything under the target URL

    print(f"\n--- Setting up Context: {context_name} for {TARGET_URL} ---")
    try:
        # Create a new context
        context_id = zap.context.new_context(context_name)
        if not context_id:
            print(f"Error: Failed to create new context '{context_name}'.")
            return
        print(f"Context '{context_name}' created with ID: {context_id}")

        # Include target URL in the context
        zap.context.include_in_context(context_name, target_regex)
        print(f"Included '{target_regex}' in context '{context_name}'.")

        # Optional: Check if it's in scope (can be verbose)
        # is_in_scope = zap.context.is_url_in_context(context_name, TARGET_URL)
        # print(f"Is '{TARGET_URL}' in context '{context_name}' scope? {is_in_scope}")

    except Exception as e:
        print(f"Error during context setup: {e}")
        return

    metrics = {}

    # --- Traditional Spider ---
    print(
        f"\n--- Starting Traditional Spider for {TARGET_URL} in context '{context_name}' ---"
    )
    spider_start_time = time.time()
    try:
        # Start the spider
        # You can add more parameters like maxchildren, recurse (default True), subtreeonly etc.
        scan_id = zap.spider.scan(url=TARGET_URL, contextname=context_name)
        if not scan_id:
            print("Error: Failed to start Traditional Spider.")
        else:
            print(f"Traditional Spider started with Scan ID: {scan_id}")
            # Poll the spider status until it's 100%
            while int(zap.spider.status(scan_id)) < 100:
                progress = int(zap.spider.status(scan_id))
                print(f"Traditional Spider progress: {progress}%")
                time.sleep(5)  # Poll every 5 seconds

            spider_end_time = time.time()
            spider_duration = spider_end_time - spider_start_time
            spider_results = zap.spider.results(scan_id)
            num_urls_found_spider = len(spider_results)

            metrics["traditional_spider"] = {
                "duration_seconds": round(spider_duration, 2),
                "urls_found": num_urls_found_spider,
            }
            print(f"Traditional Spider completed.")
            print(
                f"  Time taken: {metrics['traditional_spider']['duration_seconds']} seconds"
            )
            print(f"  URLs found: {metrics['traditional_spider']['urls_found']}")

    except Exception as e:
        print(f"Error during Traditional Spider: {e}")
        metrics["traditional_spider"] = {"error": str(e)}

    # --- AJAX Spider ---
    # Note: AJAX Spider can take significantly longer.
    # Ensure your ZAP has browsers configured for AJAX Spider if needed (usually handled by default in recent ZAP versions).
    print(
        f"\n--- Starting AJAX Spider for {TARGET_URL} in context '{context_name}' ---"
    )
    ajax_spider_start_time = time.time()
    try:
        # Start the AJAX spider
        # You can add parameters like 'inScope' (though contextname handles this), 'subtreeOnly', etc.
        # maxduration can also be set here if you want to limit the AJAX spider's own runtime.
        result = zap.ajaxSpider.scan(url=TARGET_URL, contextname=context_name)
        if result.lower() != "ok":
            print(f"Error: Failed to start AJAX Spider (Zap API returned: {result}).")
        else:
            print(f"AJAX Spider initiated.")
            # Poll the AJAX spider status until it's 'stopped'
            # AJAX Spider states: 'running', 'stopped'
            while zap.ajaxSpider.status == "running":
                print(f"AJAX Spider status: running...")
                time.sleep(10)  # Poll every 10 seconds

            ajax_spider_end_time = time.time()
            ajax_spider_duration = ajax_spider_end_time - ajax_spider_start_time
            # The number_of_results might give a count, or you can check URLs in context
            num_urls_found_ajax = zap.ajaxSpider.number_of_results

            metrics["ajax_spider"] = {
                "duration_seconds": round(ajax_spider_duration, 2),
                "urls_found": int(num_urls_found_ajax),  # Ensure it's an int
            }
            print(f"AJAX Spider completed.")
            print(f"  Time taken: {metrics['ajax_spider']['duration_seconds']} seconds")
            print(f"  URLs found (approximate): {metrics['ajax_spider']['urls_found']}")
            # For a more precise count of unique URLs in context after AJAX spider:
            # context_urls = zap.core.urls(baseurl=TARGET_URL, contextid=context_id) # or contextname=context_name
            # print(f"  Total unique URLs in context after AJAX spider: {len(context_urls)}")

    except Exception as e:
        print(f"Error during AJAX Spider: {e}")
        metrics["ajax_spider"] = {"error": str(e)}

    # --- Summary of Metrics ---
    print("\n\n--- Task Summary ---")
    print(f"Target URL: {TARGET_URL}")
    print(
        f"ZAP Context: {context_name} (ID: {context_id if 'context_id' in locals() else 'N/A'})"
    )

    if "traditional_spider" in metrics and "error" not in metrics["traditional_spider"]:
        print("\nTraditional Spider Metrics:")
        print(
            f"  Duration: {metrics['traditional_spider']['duration_seconds']} seconds"
        )
        print(f"  URLs Found: {metrics['traditional_spider']['urls_found']}")
    elif "traditional_spider" in metrics:
        print(f"\nTraditional Spider Error: {metrics['traditional_spider']['error']}")
    else:
        print("\nTraditional Spider did not run or complete.")

    if "ajax_spider" in metrics and "error" not in metrics["ajax_spider"]:
        print("\nAJAX Spider Metrics:")
        print(f"  Duration: {metrics['ajax_spider']['duration_seconds']} seconds")
        print(f"  URLs Found (by AJAX Spider): {metrics['ajax_spider']['urls_found']}")
    elif "ajax_spider" in metrics:
        print(f"\nAJAX Spider Error: {metrics['ajax_spider']['error']}")
    else:
        print("\nAJAX Spider did not run or complete.")

    print("\n--- Script Finished ---")


if __name__ == "__main__":
    main()
