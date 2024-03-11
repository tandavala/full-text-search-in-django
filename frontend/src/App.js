import React, { useState } from "react";

import "./App.css";
import Paginator from "./components/Paginator";
import { Col, Container, Row } from "react-bootstrap";

import ResultList from "./components/ResultList";
import Search from "./components/Search";
import axios from "axios";

function App() {
  const [paginatedData, setPaginatedData] = useState([]);

  const search = async (params) => {
    try {
      const response = await axios({
        method: "get",
        url: "http://localhost:8003/api/v1/catalog/wines/",
        params,
      });
      setPaginatedData(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <Container className="pt-3">
      <h1>Perusable</h1>
      <p className="lead">
        Use the controls below to peruse the wine catalog and filter the
        results.
      </p>
      <Row>
        <Col lg={4}>
          <Search search={search} />
        </Col>
        <Col lg={8}>
          {(paginatedData?.count ?? 0) > 0 && (
            <Paginator paginatedData={paginatedData} search={search} />
          )}
          <ResultList results={paginatedData?.results ?? []} />
        </Col>
      </Row>
    </Container>
  );
}

export default App;
