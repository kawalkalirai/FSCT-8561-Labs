import argparse
from datetime import datetime
from pathlib import Path

import nmap


def run_scan(target: str, ports: str, arguments: str):
    # start the actual nmap scan
    scanner = nmap.PortScanner()
    scanner.scan(target, ports, arguments)
    return scanner


def format_scan(scanner, target: str, ports: str, arguments: str) -> str:
    # basic header info for the log file
    lines = [
        "FSCT 8561 Final Exam - Day 1 Network Reconnaissance Log",
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"Target: {target}",
        f"Ports: {ports}",
        f"Arguments: {arguments}",
        "",
    ]

    if not scanner.all_hosts():
        lines.append("No reachable hosts were returned by python-nmap.")
        return "\n".join(lines)

    # go through each host and list what was found
    for host in scanner.all_hosts():
        lines.append(f"Host: {host}")
        lines.append(f"Hostname: {scanner[host].hostname()}")
        lines.append(f"State: {scanner[host].state()}")

        if not scanner[host].all_protocols():
            lines.append("No open ports detected.")
            lines.append("")
            continue

        # pull out the port/service details
        for proto in scanner[host].all_protocols():
            lines.append(f"Protocol: {proto}")
            for port in sorted(scanner[host][proto].keys()):
                details = scanner[host][proto][port]
                service = details.get("name", "unknown")
                product = details.get("product", "")
                version = details.get("version", "")
                extrainfo = details.get("extrainfo", "")
                state = details.get("state", "unknown")
                reason = details.get("reason", "n/a")
                lines.append(
                    "  "
                    f"Port {port}: state={state}, reason={reason}, "
                    f"service={service}, product={product}, version={version}, extrainfo={extrainfo}"
                )
        lines.append("")

    return "\n".join(lines)


def main():
    # lets the scan settings be passed in the terminal
    parser = argparse.ArgumentParser(
        description="Run the Day 1 python-nmap pre-flight scan and save the results to a log file."
    )
    parser.add_argument("--target", required=True, help="Server IP address or hostname to scan.")
    parser.add_argument(
        "--ports",
        default="5000",
        help="Port or port range to scan. Default: 5000",
    )
    parser.add_argument(
        "--arguments",
        default="-sT -sV",
        help="Arguments passed to nmap through python-nmap. Default: -sT -sV",
    )
    parser.add_argument(
        "--output",
        default="reconnaissance_logs/scan_results.txt",
        help="Output log path. Default: reconnaissance_logs/scan_results.txt",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # run scan and save results into the txt log
        scanner = run_scan(args.target, args.ports, args.arguments)
        log_text = format_scan(scanner, args.target, args.ports, args.arguments)
        output_path.write_text(log_text, encoding="utf-8")
        print(log_text)
        print(f"\nReconnaissance log written to: {output_path.resolve()}")
    except nmap.PortScannerError as exc:
        message = f"python-nmap error: {exc}"
        output_path.write_text(message, encoding="utf-8")
        print(message)
    except PermissionError:
        message = "Permission error: try rerunning with the privileges needed for your chosen nmap scan."
        output_path.write_text(message, encoding="utf-8")
        print(message)


if __name__ == "__main__":
    main()
