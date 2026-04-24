import os

PLANS_DIR = "/data/data/com.termux/files/home/dev/ace/plans/ace_suite_v5/"
OUTPUT_FILE = "/data/data/com.termux/files/home/dev/ace/plans/ace_suite_v5/ACE_SUITE_MASTER_SPEC.md"

def generate_master_spec():
    files = sorted([f for f in os.listdir(PLANS_DIR) if f.endswith(".md") and f != "ACE_SUITE_MASTER_SPEC.md"])
    
    # Priority sorting
    priority = ["intent.md", "RRP_SYNTHESIS.md", "01_VISION_AND_STRATEGY.md", "09_GLOSSARY_OF_COGNITION.md"]
    sorted_files = [f for f in priority if f in files] + [f for f in files if f not in priority]

    with open(OUTPUT_FILE, "w") as out:
        out.write("# 🌌 ACE SUITE: MASTER ARCHITECTURAL SPECIFICATION // v0.2.0\n\n")
        out.write("## 📑 Table of Contents\n")
        for f in sorted_files:
            title = f.replace(".md", "").replace("_", " ").title()
            anchor = f.lower().replace(".md", "").replace("_", "-")
            out.write(f"- [{title}](#{anchor})\n")
        
        out.write("\n---\n\n")

        for f in sorted_files:
            anchor = f.lower().replace(".md", "").replace("_", "-")
            out.write(f"<a name=\"{anchor}\"></a>\n")
            out.write(f"## 📄 SOURCE: {f}\n\n")
            with open(os.path.join(PLANS_DIR, f), "r") as src:
                out.write(src.read())
            out.write("\n\n---\n\n")

    print(f"[*] Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_master_spec()
