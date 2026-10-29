import { Header } from "@/components/Header";
import { Box, Heading } from "@chakra-ui/react";

export default function NotAdminPage() {
  return (
    <Box className="container" bgColor="bg.secondary">
      <Header />
      <Box mx="auto" maxW="600px" px="6" py="12">
        <Heading textAlign="center" fontSize="xl">
          このテナントの管理者ではありません
        </Heading>
      </Box>
    </Box>
  );
}
