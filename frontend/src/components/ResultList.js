import React from "react";

import ResultListItem from "./ResultListItem"; // new

// changed
function ResultList({ results }) {
  if (!results) {
    return <p>Search using the left panel.</p>;
  }

  if (results.length === 0) {
    return <p>No results found.</p>;
  }

  return (
    <div>
      {results.map((result) => (
        <ResultListItem key={result.id} result={result} />
      ))}
    </div>
  );
}

export default ResultList;
