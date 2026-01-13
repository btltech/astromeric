import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { motion } from 'framer-motion';
import './NotFoundView.css';

export default function NotFoundView() {
  return (
    <>
      <Helmet>
        <title>404 - Page Not Found | Astromeric</title>
        <meta name="description" content="Sorry, the page you're looking for doesn't exist. Return to explore astromeric." />
        <meta name="robots" content="noindex" />
      </Helmet>

      <div className="not-found-view">
        <motion.div
          className="not-found-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="cosmic-orb"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          >
            ✨
          </motion.div>

          <h1>404</h1>
          <h2>Page Not Found</h2>

          <p>
            The cosmic path you're seeking has drifted beyond the stars.
            Let's guide you back to explore the universe of possibilities.
          </p>

          <nav className="not-found-nav">
            <Link to="/" className="nav-link primary">
              🏠 Return Home
            </Link>
            <Link to="/reading" className="nav-link outline">
              🔮 Get a Reading
            </Link>
            <Link to="/learn" className="nav-link outline">
              📚 Learn More
            </Link>
            <Link to="/about" className="nav-link outline">
              ℹ️ About Us
            </Link>
          </nav>

          <motion.div
            className="stars"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            ⭐ ✨ 🌙 💫
          </motion.div>
        </motion.div>
      </div>
    </>
  );
}
