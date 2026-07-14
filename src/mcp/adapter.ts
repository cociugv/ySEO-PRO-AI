/**
 * Python Engine Adapter — Deep module owning the process seam.
 *
 * ALL TypeScript MCP tools call through this single adapter.
 * It owns: subprocess spawning, path resolution, JSON serialization,
 * timeout policy, error model, and exit code semantics.
 *
 * No tool file touches child_process, path, or timeout logic directly.
 */

import { spawn } from "child_process";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ENGINE_PATH = resolve(__dirname, "../engine/bridge.py");
const PROJECT_ROOT = resolve(__dirname, "../..");

/** Timeout for engine operations (ms) */
const DEFAULT_TIMEOUT = 120_000;

/** Uniform result from the Python engine */
export interface EngineResult {
  success: boolean;
  data: Record<string, unknown>;
  error?: string;
}

/**
 * Execute a command on the Python analysis engine.
 *
 * This is the ONLY function that spawns a subprocess.
 * All MCP tools delegate here — they never touch child_process.
 */
export async function callEngine(
  command: string,
  args: Record<string, unknown>,
  timeoutMs: number = DEFAULT_TIMEOUT
): Promise<EngineResult> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let settled = false;

    const proc = spawn("python", [ENGINE_PATH, command, JSON.stringify(args)], {
      cwd: PROJECT_ROOT,
      stdio: ["ignore", "pipe", "pipe"],
    });

    proc.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    proc.on("close", (code: number | null) => {
      if (settled) return;
      settled = true;

      if (code === 0 && stdout.trim()) {
        try {
          const parsed = JSON.parse(stdout);
          // If the engine returned an error key, surface it
          if (parsed.error) {
            resolve({ success: false, data: parsed, error: parsed.error });
          } else {
            resolve({ success: true, data: parsed });
          }
        } catch {
          // JSON parse failure — return raw output
          resolve({ success: true, data: { raw: stdout.trim() } });
        }
      } else {
        resolve({
          success: false,
          data: {},
          error: stderr.trim() || stdout.trim() || `Process exited with code ${code}`,
        });
      }
    });

    proc.on("error", (err: Error) => {
      if (settled) return;
      settled = true;
      resolve({
        success: false,
        data: {},
        error: `Failed to spawn engine: ${err.message}`,
      });
    });

    // Timeout guard
    setTimeout(() => {
      if (settled) return;
      settled = true;
      proc.kill("SIGTERM");
      resolve({
        success: false,
        data: {},
        error: `Operation timed out after ${timeoutMs / 1000}s`,
      });
    }, timeoutMs);
  });
}

/**
 * Convenience: call engine and format as MCP text content.
 */
export async function engineToMcpContent(
  command: string,
  args: Record<string, unknown>
): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  const result = await callEngine(command, args);

  const text = result.success
    ? JSON.stringify(result.data, null, 2)
    : `Error: ${result.error}`;

  return { content: [{ type: "text" as const, text }] };
}
