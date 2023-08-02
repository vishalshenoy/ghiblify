import {
  ChakraProvider,
  Heading,
  Container,
  extendTheme,
  Text,
  Input,
  Button,
  Wrap,
  Stack,
  Image,
  Link,
  SkeletonCircle,
  SkeletonText,
  Box,
  FormControl,
  FormLabel,
  Center,
  Flex,
} from "@chakra-ui/react";
import { Global } from "@emotion/react";
import React, { useState } from "react";

const customTheme = extendTheme({
  styles: {
    global: {
      body: {
        bg: "#ffffff",
      },
    },
  },
});

const App = () => {
  const [loading, setLoading] = useState(false);
  const [selectedImageURL, setSelectedImageURL] = useState("");
  const [generatedImageURL, setGeneratedImageURL] = useState("");
  const [uploadedFileName, setUploadedFileName] = useState(""); 

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onloadend = () => {
      setSelectedImageURL(reader.result);
      setUploadedFileName(file.name);
    };

    if (file) {
      reader.readAsDataURL(file);

      const formData = new FormData();
      formData.append("file", file);

      fetch("http://0.0.0.0:8000/upload_photo", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  };

  const generate = () => {
    setLoading(true);
    let path = "http://0.0.0.0:8000/get_photo/" + uploadedFileName;
    fetch(path)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.blob();
      })
      .then((blob) => {
        setGeneratedImageURL(URL.createObjectURL(blob));
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching image:", error);
        setLoading(false);
      });
  };

  return (
    <ChakraProvider theme={customTheme}>
      <Container>
        <Box borderWidth="0px" mx="0px" my="10px">
          <Text
            color="#4682A9"
            mt="50px"
            fontSize="7xl"
            fontFamily="Arial"
            fontWeight="bold"
          >
            ghiblify &#128444;
          </Text>
        </Box>
        <Box borderWidth="0px" mx="0px" mt="15px" ml="5px">
          <Text>
            an experiment which receives your photos and translates them into
            Studio Ghibli style artwork. powered by stable diffusion &#x263A;
          </Text>
        </Box>
        <Flex>
          <FormControl>
            <Input
              type="file"
              id="fileInput"
              onChange={handleImageChange}
              style={{ display: "none" }}
            />
            <Button
              mx="5px"
              my="20px"
              as="label"
              htmlFor="fileInput"
              color="#4682A9"
            >
              upload photo
            </Button>
          </FormControl>
          <Button mx="5px" my="20px" onClick={generate} color="#4682A9">
            generate
          </Button>
        </Flex>
        <Box display="flex" justifyContent="center" alignItems="center">
          {loading ? (
            <Stack>
              <Flex justifyContent="center" alignItems="center">
                <SkeletonCircle />
              </Flex>
              <Text fontSize="xs">loading!</Text>
            </Stack>
          ) : generatedImageURL ? (
            <Image src={generatedImageURL} boxShadow="lg" />
          ) : selectedImageURL ? (
            <Image src={selectedImageURL} boxShadow="lg" />
          ) : null}
        </Box>
        <Link href="https://vishalshenoy.com/" isExternal>
          <Text fontSize="xs" fontFamily="Arial" textAlign="center" my="30px">
            built by vishal
          </Text>
        </Link>
      </Container>
    </ChakraProvider>
  );
};

export default App;
