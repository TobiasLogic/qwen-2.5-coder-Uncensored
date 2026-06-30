#!/usr/bin/env python3
"""
Topic generator for the dataset pipeline (feeds topics.txt -> get.py).

You don't hand-write 1k topics. You write rich category templates + multiply
them by language/dimension, then take every unique result.

DEFAULT BEHAVIOR (TOTAL = None): take ALL deduped topics from every category.
This is what you want — it gives you the maximum quality set and lets the ratio
fall out naturally (general-heavy, which is correct for a 1.5B). Set TOTAL to an
int only if you want to hard-cap the count and sample down at RATIOS.
"""

import itertools
import random

# =================================================================
# KNOBS
# =================================================================
TOTAL  = None                                          # None = take all; int = cap+sample at RATIOS
RATIOS = {"general": 0.58, "appsec": 0.24, "pentest": 0.18}   # only used if TOTAL is an int
SEED   = 1337
OUTPUT = "topics.txt"

def expand(template, **dims):
    keys = list(dims.keys())
    return [template.format(**dict(zip(keys, combo)))
            for combo in itertools.product(*(dims[k] for k in keys))]


# =================================================================
# 1. GENERAL CODING (the ballast & specialization)
# =================================================================
def build_general():
    p = []
    GP = ["Python", "JavaScript", "Go", "Java", "C++", "Rust", "PHP", "C"]   # algo langs

    # algorithms / DS, multiplied across languages (Yield: 8 * 25 = 200)
    p += expand("Implement {algo} in {lang}", lang=GP, algo=[
        "binary search over a rotated sorted array",
        "merge sort with an explanation of its complexity",
        "quicksort with a randomized pivot",
        "Dijkstra's shortest-path algorithm",
        "a trie (prefix tree) with insert and search",
        "breadth-first search over a 2D grid maze",
        "topological sort of a directed acyclic graph",
        "a min-heap from scratch",
        "an LRU cache without using built-in helpers",
        "the edit (Levenshtein) distance between two strings",
        "a union-find structure with path compression",
        "run-length encoding and decoding",
        "a function that detects a cycle in a linked list",
        "a sliding-window longest-substring-without-repeats solver",
        "Kadane's maximum-subarray algorithm",
        "a function returning all permutations of a string",
        "a circular buffer (ring buffer)",
        "binary-tree serialization and deserialization",
        "a function to merge k sorted lists",
        "the power set of a collection",
        "A* search algorithm for pathfinding",
        "a hash map utilizing chaining for collision resolution",
        "a doubly linked list with insert, delete, and reverse",
        "the Floyd-Warshall algorithm for all-pairs shortest paths",
        "a segment tree for range sum queries"
    ])

    # Python idioms (Yield: 5 * 15 = 75)
    p += expand("Write a Python {c} that {pp}",
        c=["decorator", "context manager", "generator", "descriptor", "class-based iterator"],
        pp=[
            "measures and logs execution time of the wrapped block",
            "retries on exception with exponential backoff",
            "caches results in memory with a TTL",
            "validates arguments against the function's type hints",
            "throttles how often the function may run",
            "redirects stdout to capture output",
            "acquires and releases a file lock safely",
            "rolls back state if the block raises",
            "streams a paginated API one page at a time",
            "memoizes with bounded LRU eviction",
            "deprecation-warns when a function is called",
            "enforces that required environment variables are set",
            "buffers items and yields chunks of a specific size",
            "safely cleans up temporary database connections",
            "injects a unique request UUID into a context variable",
        ])

    # design patterns (Yield: 4 * 12 = 48)
    p += expand("Implement the {pat} pattern in {lang}",
        lang=["Python", "JavaScript", "Go", "Rust"],
        pat=["observer", "strategy", "factory", "builder", "adapter",
             "decorator", "command", "state", "repository", "dependency-injection",
             "singleton", "facade"])

    # general "write code that does X" across langs (Yield: 5 * 18 = 90)
    p += expand("Write {lang} code that {t}",
        lang=["Python", "JavaScript", "Go", "Rust", "C++"],
        t=[
            "reads a file and counts word frequency",
            "makes concurrent HTTP requests to many URLs with a concurrency cap",
            "implements a simple TCP echo server",
            "parses command-line flags and prints usage",
            "watches a directory for file changes",
            "implements a basic in-memory key-value store with expiry",
            "computes a SHA-256 hash of a file in chunks",
            "implements retry with exponential backoff and jitter",
            "parses a CSV and emits aggregated JSON",
            "implements a worker pool processing a job queue",
            "debounces and throttles a callback",
            "implements a rate limiter using a token bucket",
            "serves a static-file HTTP server with directory listing",
            "implements a simple LRU cache with a max size",
            "polls a Supabase database for new event inserts",
            "parses unstructured logs and outputs structured JSON",
            "compresses a directory into a ZIP file in memory",
            "implements a basic pub-sub event bus"
        ])

    # web / API endpoints (Yield: 7 * 18 = 126)
    p += expand("Write a {fw} implementation that {op}",
        fw=["FastAPI", "Flask", "Django REST framework", "Express (Node.js)", "Laravel", "Yii2", "Supabase Edge Function"],
        op=[
            "accepts a JSON payload and validates it against a schema",
            "handles multipart file uploads and stores them on disk",
            "implements cursor-based pagination over a Postgres database table",
            "streams a large CSV file as the response",
            "returns paginated, filterable search results using UUIDs",
            "gates access behind an API key in a request header",
            "proxies and caches responses from an upstream API",
            "exposes health and readiness probes",
            "runs a long task in the background and returns a job ID",
            "implements optimistic-concurrency updates with an ETag",
            "emits server-sent events for live updates",
            "bulk-inserts records from an uploaded JSON array",
            "implements full CRUD for a resource with validation",
            "implements login issuing a signed session token",
            "manages a Kanban board state machine (moving tickets between columns)",
            "verifies Firebase authentication tokens",
            "queries related ActiveRecord models using eager loading",
            "handles webhook verification via HMAC signatures"
        ])

    # AI / LLM Training pipeline (Yield: 18)
    p += expand("Write a {fw} script that {t}",
        fw=["PyTorch", "Hugging Face Accelerate", "JAX"],
        t=[
            "streams a large dataset like FineWeb-Edu directly during training",
            "implements gradient accumulation for training on consumer GPUs",
            "optimizes model weights for an RTX 5090 using mixed precision (fp16/bf16)",
            "calculates and logs validation loss continuously to Weights & Biases",
            "implements a custom causal self-attention mechanism from scratch",
            "loads and tokenizes a dataset for a 1.5B parameter language model"
        ])

    # Game Dev & Physics Engine (Yield: 3 * 7 = 21)
    p += expand("Write a {engine} script that {t}",
        engine=["Godot 4 (GDScript)", "Roblox (Luau)", "Minecraft Fabric (Java)"],
        t=[
            "handles smooth player velocity and momentum for a parkour game",
            "implements wall running and jumping mechanics",
            "manages seamless 3D scene transitions",
            "synchronizes multiplayer physics states with interpolation",
            "creates a dynamic UI dashboard overlay",
            "spawns and manages custom entities or non-player characters",
            "implements a raycast system for line-of-sight detection"
        ])
        
    # System & Hardware Monitoring (Yield: 3 * 6 = 18)
    p += expand("Write a {lang} system tool that {t}",
        lang=["Rust", "C", "Python"],
        t=[
            "polls the OS for current CPU and GPU temperatures",
            "monitors network bandwidth usage in real-time",
            "tracks application-specific memory consumption",
            "interfaces with the Linux /proc file system to list active processes",
            "reads system telemetry and publishes it to an IoT dashboard",
            "detects hardware changes or USB insertions via system events"
        ])

    # Databases / SQL (Yield: 18)
    p += [
        "Write a SQL query to find the second-highest salary in an employees table",
        "Write a SQL query that finds duplicate rows by a set of columns",
        "Write a SQL query using a window function to rank rows within each group",
        "Write a SQL query that computes a running total over an ordered column",
        "Write a SQL query to find users with no orders using a LEFT JOIN",
        "Write a recursive CTE that walks a parent-child category tree",
        "Write a SQL query to find the most recent record per group",
        "Write a parameterized Python upsert using psycopg2",
        "Write a SQLAlchemy function that paginates a query efficiently",
        "Write a SQL migration that adds a column with a backfilled default",
        "Write a Python script that bulk-loads a CSV into PostgreSQL with COPY",
        "Write a SQL query to detect gaps in a sequence of dates",
        "Write an indexed query and explain how to read its query plan",
        "Write a SQL query that computes a 7-day moving average",
        "Write a PostgreSQL query utilizing UUIDv4 as primary keys",
        "Write a Supabase Row Level Security (RLS) policy for user-scoped data",
        "Write a SQL query utilizing JSONB operators in PostgreSQL",
        "Write a database trigger in Postgres to automatically update a timestamp"
    ]

    # CLI, Data Processing, Testing, Bash, DevOps (Yield: ~70)
    p += expand("Write a Python CLI tool using argparse that {t}",
        t=[
            "recursively renames files matching a pattern",
            "finds duplicate files by hashing their contents",
            "bulk-resizes images in a folder",
            "tails a log file and highlights regex matches",
            "converts between JSON, YAML, and TOML",
            "generates a project scaffold from a template",
            "verifies checksums for a list of files",
            "queries a REST API and prints a results table",
            "backs up a directory to a timestamped archive",
            "diffs two directories and reports changes",
            "interfaces with the Cloudflare API to purge cache",
            "manages Vast.ai GPU instance deployments"
        ])
    
    p += expand("Write a bash script that {t}",
        t=[
            "finds and deletes files older than N days",
            "rotates and compresses logs over a size threshold",
            "monitors disk usage and alerts above a percentage",
            "backs up a PostgreSQL database to a timestamped dump",
            "restarts a service if it stops responding",
            "parses a log file and counts requests per status code",
            "syncs two directories and reports what changed",
            "shows the 10 largest files under the current directory",
            "automates SSL certificate renewal via certbot",
            "checks system uptime and writes to an external webhook"
        ])

    p += [
        "Write a multi-stage Dockerfile for a minimal Python 3.12 app",
        "Write a docker-compose file for a web app, Postgres, and Redis",
        "Write a GitHub Actions workflow that runs tests on push",
        "Write a Dockerfile that builds a static Go binary in a scratch image",
        "Write a Makefile that lints, tests, and builds a Python project",
        "Write a systemd unit for a background worker",
        "Write a GitHub Actions workflow for publishing to npm",
        "Write a Vercel deployment configuration file (vercel.json)"
    ]

    p += [
        "Write a Python script that flattens nested JSON into a CSV",
        "Write a Python script that deduplicates rows in a Parquet file",
        "Write a Python script that merges multiple CSV files on a shared key",
        "Write a Python script that streams a multi-GB file line by line",
        "Write a Python script that pivots a long-format CSV into wide format",
        "Write a Python script that detects the encoding of an unknown text file",
        "Write a Python script that masks PII (emails, phones) in a text file",
        "Write a Python script that groups records and computes running totals",
    ]
    
    p += [
        "Write pytest tests for an email-validation function",
        "Write a pytest fixture that spins up a temporary SQLite database",
        "Write parametrized pytest tests for a parser's edge cases",
        "Mock an external HTTP call in pytest using responses",
        "Write a hypothesis property-based test for a sorting function",
        "Debug and fix a Python function with an off-by-one loop error",
        "Write a test asserting a function raises the correct exception",
        "Write Jest tests for a JavaScript debounce utility",
        "Write Pest tests for a Laravel JSON API endpoint",
    ]

    # Regex, Networking, Concepts, Mini-projects (Yield: ~40)
    p += [
        "Write a regex in Python to extract all IPv4 addresses from a log file",
        "Write a regex that validates and parses ISO 8601 timestamps",
        "Write a Python function that safely strips HTML tags from a string",
        "Write a tokenizer that splits source code into identifiers and operators",
        "Write a recursive-descent parser for arithmetic expressions",
        "Write a regex to extract URLs without grabbing trailing punctuation",
        "Write a Python function that parses a User-Agent into components",
        "Write a Python function that parses a key=value config format",
        "Write a Python HTTP client with retries, timeouts, and connection pooling",
        "Implement a WebSocket echo server and client in Python",
        "Implement exponential backoff with jitter for a flaky network call",
        "Implement a circuit breaker for an unreliable downstream service",
        "Implement a retry decorator that respects a Retry-After header",
        "Implement a simple LRU-backed HTTP response cache in Python",
        "Explain and implement a context manager protocol in Python",
        "Explain and implement metaclasses in Python",
        "Explain and implement structural pattern matching in Python",
        "Build a URL shortener with a backend and SQLite storage",
        "Build a CLI todo app with JSON persistence in Python",
        "Build a Markdown-to-HTML static site generator in Python",
        "Build a simple rate-limited proxy server in Python",
        "Build a webhook receiver that validates HMAC signatures",
        "Build a directory-watcher that triggers a command on change",
    ]
    return p


# =================================================================
# 2. SECURE CODING / APPSEC
# =================================================================
def build_appsec():
    p = []
    WL = ["Python", "PHP", "Node.js", "Rust", "Go"]

    # Rewrite vulnerable code (Yield: 5 * 22 = 110)
    p += expand("Rewrite a {lang} {scenario} to be secure and explain the fix",
        lang=WL,
        scenario=[
            "login handler vulnerable to SQL injection",
            "search endpoint vulnerable to reflected XSS",
            "file-download endpoint vulnerable to path traversal",
            "URL-fetcher vulnerable to SSRF",
            "comment form vulnerable to stored XSS",
            "shell-out call vulnerable to command injection",
            "deserialization routine vulnerable to object injection",
            "template renderer vulnerable to server-side template injection",
            "redirect handler vulnerable to open redirect",
            "API route vulnerable to IDOR",
            "XML parser vulnerable to XXE",
            "password reset vulnerable to token guessing",
            "config loader with hardcoded credentials",
            "cookie/session setup with insecure flags",
            "file upload that trusts the client-supplied filename",
            "rate-limit-free login enabling credential stuffing",
            "JWT verifier that ignores the alg header",
            "query builder that concatenates user input",
            "ActiveRecord update method vulnerable to mass assignment",
            "middleware implementation vulnerable to authentication bypass",
            "CORS configuration allowing arbitrary origins",
            "WebSocket endpoint lacking origin validation"
        ])

    # Implement secure features (Yield: 5 * 15 = 75)
    p += expand("Implement secure {feat} in {lang}", lang=WL, feat=[
        "password hashing with argon2/bcrypt plus verification",
        "JWT issuance and verification with expiry and signature checks",
        "session management using signed, HttpOnly, SameSite cookies",
        "CSRF token generation and validation for a form",
        "server-side input validation and sanitization",
        "context-aware output encoding to prevent XSS",
        "a parameterized database query layer",
        "rate-limiting middleware keyed by client identity",
        "file-upload handling with type, size, and path checks",
        "a Content-Security-Policy header builder",
        "constant-time token comparison",
        "secure random token generation for reset links",
        "OAuth2 state parameter validation",
        "HMAC validation for incoming webhooks",
        "two-factor authentication (TOTP) generation and verification"
    ])

    # Harden frameworks (Yield: 6 * 10 = 60)
    p += expand("Harden a {fw} app against {vuln}",
        fw=["Django", "Laravel", "Express", "Yii2", "FastAPI", "Supabase"],
        vuln=["SQL injection", "XSS", "CSRF", "mass assignment",
              "insecure direct object references", "missing security headers",
              "unauthorized data access (via Row Level Security)", 
              "credential stuffing", "SSRF", "ReDoS"])

    # Find and fix bugs (Yield: 5 * 18 = 90)
    p += expand("Find and fix the vulnerability in a {lang} {thing}",
        lang=WL,
        thing=[
            "route that builds SQL from request params",
            "function that uses os.system with user input",
            "endpoint that renders user input into HTML",
            "file handler that joins a user path to a base directory",
            "auth check that compares tokens with ==",
            "API that returns records by a guessable numeric ID",
            "uploader that writes to a user-controlled path",
            "redirect that trusts a user-supplied next URL",
            "parser that loads untrusted serialized data",
            "login that leaks whether a username exists",
            "form that lacks CSRF protection",
            "XML endpoint that resolves external entities",
            "regex that is vulnerable to catastrophic backtracking (ReDoS)",
            "cookie setup missing Secure/HttpOnly/SameSite",
            "memory allocation routine vulnerable to buffer overflows",
            "cryptographic function using a weak cipher (e.g., DES or MD5)",
            "GraphQL endpoint vulnerable to deep query introspection",
            "API exposing sensitive environment variables in debug mode"
        ])

    p += [
        "Write a security review checklist for a PHP app handling user uploads",
        "Explain and mitigate a session-fixation vulnerability with code",
        "Write input validation for a file path that blocks directory traversal",
        "Explain how to store and rotate application secrets with a Python loader",
        "Implement a strict Content-Security-Policy and explain each directive",
        "Write a Python middleware that adds all recommended security headers",
        "Audit a login flow for username enumeration and timing leaks, then fix them",
        "Explain SameSite cookie modes and when to use each, with examples",
        "Write a PHP prepared-statement wrapper that prevents SQL injection by design",
        "Implement CSRF double-submit-cookie protection and explain the trade-offs",
        "Explain and prevent prototype pollution in a Node.js merge function",
        "Write a password-strength validator following modern NIST guidance",
        "Explain clickjacking and implement frame-busting / X-Frame-Options defenses",
        "Implement secure email-verification token flow with expiry in Python",
        "Explain TOCTOU file-handling bugs and write a safe alternative",
        "Write a function that safely renders user Markdown without XSS",
        "Explain and mitigate HTTP response splitting with code",
        "Implement audit logging for security-sensitive actions in a web app",
        "Implement Yii2 RBAC (Role-Based Access Control) checks securely",
        "Write a secure Cloudflare firewall rule setup to mitigate DDoS"
    ]
    return p


# =================================================================
# 3. PENTEST TOOLING (authorized testing / CTF / lab)
# =================================================================
def build_pentest():
    p = []
    
    # Tool building (Yield: 4 * 16 = 64)
    p += expand("Write a {lang} tool that {t}",
        lang=["Python", "Go", "Rust", "C++"],
        t=[
            "performs a TCP connect port scan over a range",
            "grabs service banners from open ports",
            "enumerates subdomains from a wordlist via DNS",
            "brute-forces directories on a web server from a wordlist",
            "fingerprints a web server from HTTP response headers",
            "discovers live hosts on a subnet via ping sweep",
            "performs reverse DNS lookups across an IP range",
            "enumerates virtual hosts by varying the Host header",
            "detects the CMS and tech stack of a target URL",
            "checks targets for missing/misconfigured security headers",
            "crawls a site and extracts links, forms, and inputs",
            "resolves and probes a list of domains concurrently",
            "detects anonymous FTP and SMB shares",
            "scrapes TLS/SSL certificates to find alternate names",
            "monitors a target domain for DNS record changes over time",
            "automates subdomain takeover vulnerability checks"
        ])

    # Target specific fuzzing (Yield: 18)
    p += expand("Write a Python script that {t}",
        t=[
            "fuzzes a URL parameter with a payload list and flags anomalies",
            "tests a login form for error-based SQL injection",
            "detects reflected XSS by injecting and locating payloads",
            "tests for command injection in a request parameter",
            "enumerates IDOR by iterating IDs and diffing responses",
            "brute-forces HTTP basic auth from a credential list",
            "discovers hidden endpoints by fuzzing common paths",
            "tests a redirect parameter for open-redirect behavior",
            "detects server-side template injection (SSTI)",
            "tests for local file inclusion via a path parameter",
            "generates a CSRF proof-of-concept for a target form",
            "checks URLs for exposed backup/config files (.bak, .git, .env)",
            "extracts EXIF and document metadata for OSINT",
            "scrapes a site for email addresses and usernames",
            "tests CORS configurations for origin reflections",
            "bypasses rate limits by rotating X-Forwarded-For headers",
            "fuzzes GraphQL endpoints for unauthenticated queries",
            "detects potential cache poisoning vulnerabilities"
        ])

    # Proof of Concepts (Yield: 18)
    p += expand("Write a Python proof-of-concept that demonstrates {vc} on a test target",
        vc=[
            "boolean-based blind SQL injection", "time-based blind SQL injection",
            "reflected XSS", "stored XSS", "SSRF to an internal endpoint",
            "XXE file disclosure", "server-side template injection",
            "insecure deserialization", "an open-redirect chain",
            "JWT 'alg: none' bypass", "path-traversal file read",
            "HTTP request smuggling detection", "CRLF injection",
            "host-header injection", "a race condition in a request flow",
            "XMLRPC brute force attack", "NoSQL injection",
            "LDAP injection"
        ])

    # Network / Scapy (Yield: 10)
    p += [
        "Write a Scapy script that performs an ARP scan of the local subnet",
        "Write a Scapy script that sniffs and filters HTTP requests",
        "Write a Scapy script that crafts and sends a custom TCP SYN packet",
        "Write a Scapy script that detects ARP spoofing on the network",
        "Write a Scapy-based traceroute implementation",
        "Write a Python tool that passively maps hosts seen on the network",
        "Write a Python script that captures and logs DNS queries",
        "Write a Scapy script to detect unauthorized DHCP servers",
        "Write a Python tool to perform a UDP sweep",
        "Write a Scapy script to analyze and parse ICMP traffic"
    ]

    # Bash Recon (Yield: 3 * 10 = 30)
    p += expand("Write a bash {kind} that {t}",
        kind=["one-liner", "script", "alias collection"],
        t=[
            "performs a ping sweep across a /24 subnet",
            "checks if a TCP port is open using /dev/tcp",
            "extracts unique IP addresses from a log file",
            "parses nmap greppable output into host:port",
            "resolves a list of domains to IPs in parallel",
            "fuzzes a list of paths against a URL with curl",
            "filters out out-of-scope IPs from a recon list",
            "downloads and deduplicates public wordlists",
            "runs parallel whois lookups and greps for org names",
            "monitors network interfaces via tcpdump for specific ports"
        ])

    # Parsers & Processing (Yield: 8)
    p += [
        "Write a Python parser for nmap XML that lists open ports per host",
        "Write a Python parser for masscan JSON output",
        "Write a Python script that diffs two nmap scans for new open ports",
        "Write a parser that turns gobuster output into a structured report",
        "Write a Python tool that merges multiple recon outputs into one report",
        "Write a Python script that parses a Burp/ZAP export and summarizes findings",
        "Write a Python script that ingests Nikto output into a SQLite database",
        "Write a Python utility to parse Amass JSON output for subdomains"
    ]

    # Crypto & Hash analysis (Yield: 10)
    p += [
        "Write a Python script that runs a dictionary attack on MD5 hashes from a wordlist",
        "Write a Python tool that identifies a hash type from its format",
        "Write a Python script that brute-forces a short numeric PIN against a check function",
        "Write a Python tool that tests a JWT for the 'alg: none' bypass",
        "Write a Python script that detects and decodes base64/hex/ROT13 blobs",
        "Write a Python tool that cracks a Caesar/substitution cipher by frequency analysis",
        "Write a Python script that checks passwords against the HIBP k-anonymity API",
        "Write a Python tool that audits a password list for weak/common entries",
        "Write a Python script to verify bcrypt hashes against a breached list",
        "Write a Python utility to forge insecure JWT tokens for testing"
    ]

    # Wordlists & Automation (Yield: 10)
    p += [
        "Write a Python script that generates a targeted wordlist from user info via mangling rules",
        "Write a Python tool that permutes and case-varies a base wordlist",
        "Write a Python script that generates encoded XSS payload variants for filter testing",
        "Write a Python tool that builds a fuzzing wordlist from a target's own pages",
        "Write a Python script that generates SQLi test payloads for different DB engines",
        "Write a Python script that generates custom directories for API fuzzing",
        "Write a Python tool that automates a recon workflow and outputs a markdown report",
        "Write a Python script that schedules recurring scans and diffs results over time",
        "Write a Python tool that normalizes findings from several scanners into one schema",
        "Write a Python script that screenshots a list of live web hosts for triage"
    ]

    return p


# =================================================================
# ASSEMBLE
# =================================================================
def main():
    random.seed(SEED)
    builders = {"general": build_general, "appsec": build_appsec, "pentest": build_pentest}

    selected, seen, report = [], set(), {}
    for name, build in builders.items():
        pool = list(dict.fromkeys(build()))
        random.shuffle(pool)
        take = pool if TOTAL is None else pool[:round(TOTAL * RATIOS[name])]
        kept = 0
        for t in take:
            if t not in seen:
                seen.add(t); selected.append(t); kept += 1
        report[name] = (kept, len(pool))

    random.shuffle(selected)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(selected) + "\n")

    total = len(selected)
    print(f"Wrote {total} topics -> {OUTPUT}\n")
    print(f"{'category':<10} {'kept':>6} {'pool':>6} {'share':>7}")
    for name, (kept, pool_n) in report.items():
        print(f"{name:<10} {kept:>6} {pool_n:>6} {kept/total*100:>6.1f}%")


if __name__ == "__main__":
    main()
