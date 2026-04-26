import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";


export default async function LoginPage({ searchParams }) {
  const cookieStore = await cookies();
  const hasSession = cookieStore.get("mxsense_session")?.value === "active";

  if (hasSession) {
    redirect("/dashboard");
  }

  const params = await Promise.resolve(searchParams);
  const errorParam = params?.error;
  let errorMessage = "";
  if (typeof errorParam === "string" && errorParam.trim()) {
    try {
      errorMessage = decodeURIComponent(errorParam);
    } catch {
      errorMessage = errorParam;
    }
  }

  return (
    <main>
      <div className="login-screen">
        <div className="login-card">
          <div className="login-copy">
            <h1>Sign in</h1>
            <p>Use your MXSense account.</p>
          </div>

          {errorMessage ? (
            <p className="login-error" role="alert">
              {errorMessage}
            </p>
          ) : null}

          <form action="/auth/sign-in" className="login-form" method="post">
            <div className="login-field">
              <span>USERNAME</span>
              <input autoComplete="username" name="username" type="text" />
            </div>

            <div className="login-field">
              <span>PASSWORD</span>
              <input autoComplete="current-password" name="password" type="password" />
            </div>

            <button className="ui-button ui-button-rect login-button" type="submit">
              Sign in
            </button>
          </form>

          <div className="login-footer">
            No account? <Link href="/sign-up">Create one</Link>
          </div>
        </div>
      </div>
    </main>
  );
}
