import Link from "next/link";


export default function NotFound() {
  return (
    <main className="slide-page">
      <section className="console-stage">
        <div className="console-header">
          <span className="header-badge">Missing</span>
          <h1>MxSense Adaptive Intelligence Systems</h1>
        </div>
        <section className="services-panel">
          <div className="services-header">
            <h3>That workspace view is not mapped yet.</h3>
            <p>
              The current frontend only exposes the module navigation defined from the supplied
              PPTX reference.
            </p>
          </div>
          <div className="footer-link-row">
            <Link className="ui-button ui-button-pill footer-link" href="/dashboard">
              Return to frontend shell
            </Link>
          </div>
        </section>
      </section>
    </main>
  );
}
