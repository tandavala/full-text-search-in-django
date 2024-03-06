import { Formik } from "formik";
import { Button, Col, Form, Row } from "react-bootstrap";

function Search({ search }) {
  const onSubmit = async (values, actions) => {
    await search({
      country: values.country,
      limit: 10,
      offset: 0,
      points: values.points,
      query: values.query,
    });
  };

  return (
    <Formik
      initialValues={{
        country: "",
        points: "",
        query: "",
      }}
      onSubmit={onSubmit}
    >
      {({ handleChange, handleSubmit, values }) => (
        <Form noValidate onSubmit={handleSubmit}>
          <Form.Group controlId="country">
            <Form.Label>Country</Form.Label>
            <Col>
              <Form.Control
                type="text"
                name="country"
                placeholder="Enter a country (e.g. US)"
                value={values.country}
                onChange={handleChange}
              />
              <Form.Text className="text-muted">
                Filters search results by country.
              </Form.Text>
            </Col>
          </Form.Group>
          <Form.Group>
            <Form.Label htmlFor="points">Points</Form.Label>
            <Col>
              <Form.Control
                id="points"
                type="number"
                min="1"
                max="100"
                name="points"
                placeholder="Enter points (e.g. 92)"
                value={values.points}
                onChange={handleChange}
              />
              <Form.Text className="text-muted">
                Filters search results by points.
              </Form.Text>
            </Col>
          </Form.Group>

          <Form.Group controlId="query">
            <Form.Label>Query</Form.Label>
            <Col>
              <Form.Control
                type="text"
                name="query"
                placeholder="Enter a search term (e.g. cabernet)"
                value={values.query}
                onChange={handleChange}
              />
              <Form.Text className="text-muted">
                Searches for query in variety, winery, and description.
              </Form.Text>
            </Col>
          </Form.Group>
          <Form.Group as={Row}>
            <Col>
              <Button type="submit" variant="primary">
                Search
              </Button>
            </Col>
          </Form.Group>
        </Form>
      )}
    </Formik>
  );
}

export default Search;
