import React from "react";

import { sanitize } from "dompurify";
import { Card } from "react-bootstrap";

function ResultListItem({ result }) {
  return (
    <Card className="mb-3">
      <Card.Body>
        <Card.Title
          dangerouslySetInnerHTML={{
            __html: `${sanitize(result.winery)} ${sanitize(result.variety)}`,
          }}
        ></Card.Title>
        <Card.Subtitle className="mb-2 text-muted">
          {result.country} | {result.points} Points | ${result.price}
        </Card.Subtitle>
        <Card.Text
          dangerouslySetInnerHTML={{ __html: sanitize(result.description) }}
        />
      </Card.Body>
    </Card>
  );
}

export default ResultListItem;
